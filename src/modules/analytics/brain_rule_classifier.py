from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset



@dataclass
class TokenVocab:
    token_to_id: Dict[str, int]
    id_to_token: Dict[int, str]

    pad_token: str = "<PAD>"
    unk_token: str = "<UNK>"
    bos_token: str = "<BOS>"
    eos_token: str = "<EOS>"

    @property
    def pad_id(self) -> int:
        return self.token_to_id[self.pad_token]

    @property
    def unk_id(self) -> int:
        return self.token_to_id[self.unk_token]

    def encode_tokens(self, tokens: List[str], *, max_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
          input_ids [max_len], attention_mask [max_len]
        """

        # +2 for BOS/EOS, plus padding
        tokens = tokens[: max_len - 2]
        input_tokens = [self.bos_token] + tokens + [self.eos_token]
        ids = [self.token_to_id.get(t, self.unk_id) for t in input_tokens]
        attn_mask = [1] * len(ids)

        while len(ids) < max_len:
            ids.append(self.pad_id)
            attn_mask.append(0)

        return torch.tensor(ids, dtype=torch.long), torch.tensor(attn_mask, dtype=torch.float32)


def build_vocab_from_tokens(token_sequences: Iterable[str], *, min_token_freq: int = 1) -> TokenVocab:
    # token_sequences is CSV column values: "tok1 tok2 tok3"
    from collections import Counter

    counter: Counter[str] = Counter()
    for seq in token_sequences:
        if not isinstance(seq, str) or not seq:
            continue
        toks = [t for t in seq.split(" ") if t]
        counter.update(toks)

    # Special tokens first
    specials = ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]
    token_to_id: Dict[str, int] = {tok: i for i, tok in enumerate(specials)}

    for tok, freq in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        if freq < min_token_freq:
            continue
        if tok in token_to_id:
            continue
        token_to_id[tok] = len(token_to_id)

    id_to_token = {i: t for t, i in token_to_id.items()}
    return TokenVocab(token_to_id=token_to_id, id_to_token=id_to_token)


class BrainRuleDataset(Dataset):
    def __init__(self, df: pd.DataFrame, *, max_seq_len: int):
        self.df = df.reset_index(drop=True)
        self.max_seq_len = max_seq_len

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.df.iloc[idx]
        tokens_str = row.get("tokens", "")
        tokens = [t for t in str(tokens_str).split(" ") if t]
        y = float(row.get("is_good_for_submit", 0.0))
        return {"tokens": tokens, "y": y}


class ExpressionRuleClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        *,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dim_feedforward: int = 256,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(d_model, 1)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        input_ids: [B, L]
        attention_mask: [B, L] float 0/1
        """
        x = self.embedding(input_ids)  # [B, L, d]
        x = self.dropout(x)

        # Transformer expects src_key_padding_mask: True means "ignore"
        key_padding_mask = attention_mask < 0.5
        h = self.encoder(x, src_key_padding_mask=key_padding_mask)  # [B, L, d]

        # Mean pool on non-pad tokens
        mask = attention_mask.unsqueeze(-1)  # [B, L, 1]
        summed = (h * mask).sum(dim=1)
        denom = mask.sum(dim=1).clamp(min=1.0)
        pooled = summed / denom
        logits = self.head(pooled).squeeze(-1)  # [B]
        return logits


def _collate_with_vocab(batch: List[Dict[str, Any]], vocab: TokenVocab, *, max_seq_len: int) -> Dict[str, Any]:
    input_ids_list = []
    attn_list = []
    y_list = []
    for item in batch:
        input_ids, attn_mask = vocab.encode_tokens(item["tokens"], max_len=max_seq_len)
        input_ids_list.append(input_ids)
        attn_list.append(attn_mask)
        y_list.append(item["y"])
    return {
        "input_ids": torch.stack(input_ids_list, dim=0),
        "attention_mask": torch.stack(attn_list, dim=0),
        "y": torch.tensor(y_list, dtype=torch.float32),
    }


def train_rule_classifier(
    dataset_csv_path: str,
    *,
    output_dir: str,
    max_seq_len: int = 256,
    d_model: int = 64,
    nhead: int = 4,
    num_layers: int = 2,
    batch_size: int = 32,
    lr: float = 1e-3,
    weight_decay: float = 1e-2,
    epochs: int = 5,
    val_ratio: float = 0.15,
    seed: int = 42,
    device: Optional[str] = None,
    monitor_gpu_log_path: Optional[str] = None,
) -> str:
    """
    Trains a binary classifier: P(is_good_for_submit=1 | expression_tokens)
    Saves:
      - model.pt (state dict + model config)
      - vocab.json
    """
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(dataset_csv_path)
    if "is_good_for_submit" not in df.columns:
        raise ValueError("Dataset CSV must contain column: is_good_for_submit")
    if "tokens" not in df.columns:
        raise ValueError("Dataset CSV must contain column: tokens")

    df = df.dropna(subset=["tokens", "is_good_for_submit"])
    df["is_good_for_submit"] = df["is_good_for_submit"].astype(float)

    # Basic train/val split
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    val_size = int(len(df) * val_ratio)
    val_df = df.iloc[:val_size].copy() if val_size > 0 else df.iloc[0:0].copy()
    train_df = df.iloc[val_size:].copy() if val_size > 0 else df.copy()

    vocab = build_vocab_from_tokens(train_df["tokens"].values.tolist())

    train_ds = BrainRuleDataset(train_df, max_seq_len=max_seq_len)
    val_ds = BrainRuleDataset(val_df, max_seq_len=max_seq_len) if len(val_df) else None

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda b: _collate_with_vocab(b, vocab, max_seq_len=max_seq_len),
    )

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = ExpressionRuleClassifier(
        vocab_size=len(vocab.token_to_id),
        d_model=d_model,
        nhead=nhead,
        num_layers=num_layers,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.BCEWithLogitsLoss()

    # Optional GPU monitoring is done outside; here we just keep the param for wiring.
    _ = monitor_gpu_log_path

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            y = batch["y"].to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item())

        avg_loss = total_loss / max(1, len(train_loader))

        if val_ds is not None and len(val_ds) > 0:
            model.eval()
            correct = 0
            total = 0
            val_loader = DataLoader(
                val_ds,
                batch_size=batch_size,
                shuffle=False,
                collate_fn=lambda b: _collate_with_vocab(b, vocab, max_seq_len=max_seq_len),
            )
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch["input_ids"].to(device)
                    attention_mask = batch["attention_mask"].to(device)
                    y = batch["y"].to(device)
                    logits = model(input_ids, attention_mask)
                    probs = torch.sigmoid(logits)
                    pred = probs >= 0.5
                    correct += int((pred.float() == y).sum().item())
                    total += y.numel()
            acc = correct / max(1, total)
        else:
            acc = None

        # Minimal logging to stdout (training can be long-running)
        print(f"[train] epoch={epoch+1}/{epochs} loss={avg_loss:.4f} val_acc={acc}")

    vocab_path = os.path.join(output_dir, "vocab.json")
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump({"token_to_id": vocab.token_to_id}, f, ensure_ascii=False)

    model_path = os.path.join(output_dir, "model.pt")
    payload = {
        "model_state_dict": model.state_dict(),
        "model_config": {"vocab_size": len(vocab.token_to_id), "d_model": d_model, "nhead": nhead, "num_layers": num_layers},
        "max_seq_len": max_seq_len,
    }
    torch.save(payload, model_path)
    return model_path

