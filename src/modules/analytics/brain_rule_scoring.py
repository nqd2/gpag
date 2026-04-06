from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

import torch

from modules.analytics.brain_rule_classifier import ExpressionRuleClassifier, TokenVocab
from modules.analytics.brain_rule_schema import tokenize_expression


@dataclass
class RuleClassifierArtifacts:
    model: ExpressionRuleClassifier
    vocab: TokenVocab
    max_seq_len: int
    device: str


def load_rule_classifier(model_path: str, *, device: Optional[str] = None) -> RuleClassifierArtifacts:
    payload = torch.load(model_path, map_location="cpu")
    model_config = payload.get("model_config") or {}
    max_seq_len = int(payload.get("max_seq_len") or 256)

    # Load vocab.json from same output dir
    import os

    out_dir = os.path.dirname(model_path)
    vocab_path = os.path.join(out_dir, "vocab.json")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab_json = json.load(f)
    vocab = TokenVocab(token_to_id=vocab_json["token_to_id"], id_to_token={int(i): t for t, i in vocab_json["token_to_id"].items()})

    vocab_size = len(vocab.token_to_id)
    model = ExpressionRuleClassifier(
        vocab_size=vocab_size,
        d_model=int(model_config.get("d_model", 64)),
        nhead=int(model_config.get("nhead", 4)),
        num_layers=int(model_config.get("num_layers", 2)),
    )
    model.load_state_dict(payload["model_state_dict"])

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return RuleClassifierArtifacts(model=model, vocab=vocab, max_seq_len=max_seq_len, device=device)


@torch.no_grad()
def score_expression_probability(artifacts: RuleClassifierArtifacts, expression: str) -> float:
    tokens = tokenize_expression(expression)
    input_ids, attention_mask = artifacts.vocab.encode_tokens(tokens, max_len=artifacts.max_seq_len)
    input_ids = input_ids.unsqueeze(0).to(artifacts.device)
    attention_mask = attention_mask.unsqueeze(0).to(artifacts.device)
    logits = artifacts.model(input_ids, attention_mask)
    prob = torch.sigmoid(logits).item()
    return float(prob)

