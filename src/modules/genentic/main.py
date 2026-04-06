#!/usr/bin/env python3
"""Main entry point for Alpha Genetic Pipeline."""

import argparse
import sys

from modules.genentic.orchestrator import AlphaPipeline, PipelineConfig


def main():
    parser = argparse.ArgumentParser(description="Alpha Genetic Pipeline for WorldQuant BRAIN")
    parser.add_argument("--target", type=int, default=50, help="Target number of alphas")
    parser.add_argument("--generations", type=int, default=50, help="Max generations")
    parser.add_argument("--population", type=int, default=200, help="Population size")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--simulate", action="store_true", default=True, help="Simulate submission")
    args = parser.parse_args()

    config = PipelineConfig(
        population_size=args.population,
        generations=args.generations,
        output_dir=args.output,
    )
    pipeline = AlphaPipeline(config)
    summary = pipeline.run(target_alphas=args.target, max_generations=args.generations)

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Elapsed: {summary['elapsed_seconds']:.1f}s")
    print(f"Generations: {summary['total_generations']}")
    print(f"Alphas passed: {summary['total_alphas_passed']}")
    print(f"Submitted: {summary['submission_summary'].get('total_submitted', 0)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
