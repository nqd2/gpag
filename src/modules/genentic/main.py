#!/usr/bin/env python3
"""Main entry point for Alpha Genetic Pipeline."""

import argparse
import logging
import sys

from config import defaults
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


def main():
    parser = argparse.ArgumentParser(description="Alpha Genetic Pipeline for WorldQuant BRAIN")
    parser.add_argument("--target", type=int, default=defaults.TARGET, help="Target number of alphas")
    parser.add_argument("--generations", type=int, default=defaults.GENERATIONS, help="Max generations")
    parser.add_argument("--population", type=int, default=defaults.POPULATION, help="Population size")
    parser.add_argument("--output", type=str, default=defaults.OUTPUT_DIR, help="Output directory")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    parser.add_argument(
        "--is-mock",
        type=_str2bool,
        nargs="?",
        const=True,
        default=defaults.IS_MOCK,
        help="Use mock flow (genetic + local simulator + mock submit). Default is real flow.",
    )

    parser.add_argument(
        "--ml-model-path",
        type=str,
        default="",
        help="Optional path to trained model.pt for ML-guided candidate selection.",
    )
    parser.add_argument(
        "--ml-candidate-pool-size",
        type=int,
        default=0,
        help="If > 0, only simulate top-N candidates selected by ML model.",
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

    config = PipelineConfig(
        population_size=args.population,
        generations=args.generations,
        output_dir=args.output,
        is_mock=args.is_mock,
        log_level=args.log_level,
        ml_model_path=args.ml_model_path or None,
        ml_candidate_pool_size=args.ml_candidate_pool_size,
    )
    logging.getLogger("AlphaPipeline").info(
        "Starting pipeline mode=%s target=%s generations=%s population=%s",
        "mock" if args.is_mock else "real",
        args.target,
        args.generations,
        args.population,
    )
    pipeline = AlphaPipeline(config)
    summary = pipeline.run(target_alphas=args.target, max_generations=args.generations)

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Elapsed: {summary['elapsed_seconds']:.1f}s")
    print(f"Generations: {summary['total_generations']}")
    print(f"Mode: {'mock' if args.is_mock else 'real'}")
    print(f"Alphas passed: {summary['total_alphas_passed']}")
    print(f"Submitted: {summary['submission_summary'].get('total_submitted', 0)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
