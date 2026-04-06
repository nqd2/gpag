from __future__ import annotations

import argparse
import os
import time

from modules.analytics.gpu_monitor import NvidiaSmiLogger


def main() -> int:
    parser = argparse.ArgumentParser(description="Continuously log `nvidia-smi` metrics to a CSV file.")
    parser.add_argument("--output", type=str, required=True, help="CSV output path")
    parser.add_argument("--interval-sec", type=float, default=1.0, help="Sampling interval (seconds)")
    parser.add_argument("--duration-sec", type=float, default=0.0, help="If > 0: stop after this many seconds")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    logger = NvidiaSmiLogger(args.output, interval_sec=args.interval_sec)

    # Start logging thread
    logger.__enter__()
    try:
        if args.duration_sec and args.duration_sec > 0:
            time.sleep(args.duration_sec)
        else:
            while True:
                time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        logger.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

