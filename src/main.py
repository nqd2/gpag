#!/usr/bin/env python3
"""
Full active-learning pipeline runner.

Flow per round:
  1) Run genetic pipeline (WQB simulate/submit).
  2) Harvest BRAIN IS rule pass/fail from output/simulation_results.
  3) Build ML dataset.
  4) Train rule classifier (optionally with nvidia-smi monitoring).

Default repetition is 10 rounds.
"""

from __future__ import annotations

import argparse
import logging
import os
from typing import Optional

from config import defaults
from modules.analytics.brain_ml_dataset_builder import build_rule_dataset
from modules.analytics.brain_rules_harvester import harvest_brain_rules_from_simulation_results
from modules.analytics.gpu_monitor import start_nvidia_smi_logger
from modules.analytics.brain_rule_classifier import train_rule_classifier
from modules.genentic.orchestrator import AlphaPipeline, PipelineConfig


def _str2bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def _setup_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


def run_round(
    round_idx: int,
    *,
    output_dir: str,
    target: int,
    generations: int,
    population: int,
    is_mock: bool,
    log_level: str,
    only_submitted: bool,
    previous_model_path: Optional[str],
    ml_candidate_pool_size: int,
    train_epochs: int,
    train_batch_size: int,
    train_lr: float,
    train_weight_decay: float,
    train_val_ratio: float,
    seed: int,
    monitor_gpu: bool,
) -> str:
    logger = logging.getLogger("full_pipeline")

    round_dir = os.path.join(output_dir, "active_learning", f"round_{round_idx:02d}")
    os.makedirs(round_dir, exist_ok=True)

    logger.info("=== Round %s start ===", round_idx)

    # 1) Genetic pipeline
    config = PipelineConfig(
        population_size=population,
        generations=generations,
        output_dir=output_dir,
        is_mock=is_mock,
        log_level=log_level,
        ml_model_path=previous_model_path,
        ml_candidate_pool_size=ml_candidate_pool_size if previous_model_path else 0,
    )
    pipeline = AlphaPipeline(config)
    summary = pipeline.run(target_alphas=target, max_generations=generations)
    logger.info(
        "Round=%s pipeline done passed=%s submitted=%s",
        round_idx,
        summary.get("total_alphas_passed"),
        (summary.get("submission_summary") or {}).get("total_submitted"),
    )

    # 2) Harvest rules
    simulation_results_dir = os.path.join(output_dir, "simulation_results")
    rules_jsonl = os.path.join(round_dir, "brain_rules.jsonl")
    outcomes = harvest_brain_rules_from_simulation_results(
        simulation_results_dir,
        output_jsonl_path=rules_jsonl,
        only_submitted=only_submitted,
    )
    if not outcomes and only_submitted:
        logger.warning(
            "Round=%s no submitted alphas yet; fallback to only_submitted=False for dataset build.",
            round_idx,
        )
        outcomes = harvest_brain_rules_from_simulation_results(
            simulation_results_dir,
            output_jsonl_path=rules_jsonl,
            only_submitted=False,
        )

    # 3) Dataset build
    dataset_csv = os.path.join(round_dir, "brain_dataset.csv")
    build_rule_dataset(
        simulation_results_dir,
        output_csv_path=dataset_csv,
        only_submitted=only_submitted and bool(outcomes),
    )
    logger.info("Round=%s dataset built path=%s", round_idx, dataset_csv)

    # 4) Model training
    model_out_dir = os.path.join(round_dir, "ml_rule_model")
    os.makedirs(model_out_dir, exist_ok=True)
    gpu_log = os.path.join(model_out_dir, "gpu_usage.csv")

    gpu_monitor_ctx = None
    if monitor_gpu:
        gpu_monitor_ctx = start_nvidia_smi_logger(gpu_log, interval_sec=1.0)
        gpu_monitor_ctx.__enter__()

    try:
        model_path = train_rule_classifier(
            dataset_csv,
            output_dir=model_out_dir,
            epochs=train_epochs,
            batch_size=train_batch_size,
            lr=train_lr,
            weight_decay=train_weight_decay,
            val_ratio=train_val_ratio,
            seed=seed + round_idx,
            monitor_gpu_log_path=gpu_log if monitor_gpu else None,
        )
    finally:
        if gpu_monitor_ctx is not None:
            gpu_monitor_ctx.close()

    logger.info("Round=%s model saved=%s", round_idx, model_path)
    logger.info("=== Round %s end ===", round_idx)
    return model_path


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run full active-learning pipeline loop.")
    parser.add_argument("--repetition", type=int, default=defaults.REPETITION, help="Number of active-learning rounds.")
    parser.add_argument("--target", type=int, default=defaults.TARGET, help="Target number of passed alphas per round.")
    parser.add_argument("--generations", type=int, default=defaults.GENERATIONS, help="Max generations per round.")
    parser.add_argument("--population", type=int, default=defaults.POPULATION, help="Population size per round.")
    parser.add_argument("--output", type=str, default=defaults.OUTPUT_DIR, help="Base output directory.")
    parser.add_argument("--log-level", type=str, default=defaults.LOG_LEVEL, choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--is-mock", type=_str2bool, nargs="?", const=True, default=defaults.IS_MOCK)
    parser.add_argument(
        "--only-submitted",
        type=_str2bool,
        nargs="?",
        const=True,
        default=defaults.ONLY_SUBMITTED,
        help="If true, dataset uses submitted alphas only; auto-fallback if empty.",
    )
    parser.add_argument("--ml-candidate-pool-size", type=int, default=defaults.ML_CANDIDATE_POOL_SIZE, help="Top-N candidates simulated when ML model exists.")
    parser.add_argument("--train-epochs", type=int, default=defaults.TRAIN_EPOCHS)
    parser.add_argument("--train-batch-size", type=int, default=defaults.TRAIN_BATCH_SIZE)
    parser.add_argument("--train-lr", type=float, default=defaults.TRAIN_LR)
    parser.add_argument("--train-weight-decay", type=float, default=defaults.TRAIN_WEIGHT_DECAY)
    parser.add_argument("--train-val-ratio", type=float, default=defaults.TRAIN_VAL_RATIO)
    parser.add_argument("--seed", type=int, default=defaults.SEED)
    parser.add_argument(
        "--monitor-gpu",
        type=_str2bool,
        nargs="?",
        const=True,
        default=defaults.MONITOR_GPU,
        help="Log nvidia-smi metrics during model training.",
    )
    args = parser.parse_args(argv)

    _setup_logging(args.log_level)
    logger = logging.getLogger("full_pipeline")
    logger.info("Starting full pipeline repetition=%s output=%s", args.repetition, args.output)

    os.makedirs(args.output, exist_ok=True)

    model_path: Optional[str] = None
    for round_idx in range(1, args.repetition + 1):
        model_path = run_round(
            round_idx,
            output_dir=args.output,
            target=args.target,
            generations=args.generations,
            population=args.population,
            is_mock=args.is_mock,
            log_level=args.log_level,
            only_submitted=args.only_submitted,
            previous_model_path=model_path,
            ml_candidate_pool_size=args.ml_candidate_pool_size,
            train_epochs=args.train_epochs,
            train_batch_size=args.train_batch_size,
            train_lr=args.train_lr,
            train_weight_decay=args.train_weight_decay,
            train_val_ratio=args.train_val_ratio,
            seed=args.seed,
            monitor_gpu=args.monitor_gpu,
        )

    logger.info("Full pipeline complete. final_model=%s", model_path)
    print(f"Done. Final model: {model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

