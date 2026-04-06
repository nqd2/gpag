from __future__ import annotations

import csv
import os
import shutil
import subprocess
import threading
import time
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Optional


@dataclass
class NvidiaSmiRow:
    ts: float
    utilization_gpu: Optional[int] = None
    utilization_mem: Optional[int] = None
    memory_used_mib: Optional[int] = None
    memory_total_mib: Optional[int] = None


class NvidiaSmiLogger(AbstractContextManager):
    def __init__(self, output_csv_path: str, *, interval_sec: float = 1.0):
        self.output_csv_path = output_csv_path
        self.interval_sec = interval_sec
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._nvidia_smi = shutil.which("nvidia-smi")

    def __enter__(self) -> "NvidiaSmiLogger":
        os.makedirs(os.path.dirname(self.output_csv_path) or ".", exist_ok=True)
        # Start logging thread
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _run(self) -> None:
        if not self._nvidia_smi:
            # Nothing to log
            with open(self.output_csv_path, "w", encoding="utf-8") as f:
                f.write("ts,available\n")
                f.write(f"{time.time()},0\n")
            return

        # Query a single GPU line; format without headers for stable parsing.
        # Utilization values are percentages.
        cmd = [
            self._nvidia_smi,
            "--query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ]
        with open(self.output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ts", "utilization_gpu_pct", "utilization_mem_pct", "memory_used_mib", "memory_total_mib"])
            while not self._stop_event.is_set():
                ts = time.time()
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if proc.returncode != 0:
                        writer.writerow([ts, "", "", "", ""])
                    else:
                        # If multiple GPUs exist, take the first line to keep dataset small.
                        line = (proc.stdout or "").strip().splitlines()[0] if (proc.stdout or "").strip() else ""
                        parts = [p.strip() for p in line.split(",")] if line else []
                        row = parts + ["", "", "", ""]
                        writer.writerow([ts, row[0], row[1], row[2], row[3]])
                    f.flush()
                except Exception:
                    writer.writerow([ts, "", "", "", ""])
                    f.flush()

                # Sleep with stop check
                waited = 0.0
                while waited < self.interval_sec and not self._stop_event.is_set():
                    time.sleep(min(0.2, self.interval_sec - waited))
                    waited += 0.2


def start_nvidia_smi_logger(output_csv_path: str, *, interval_sec: float = 1.0) -> NvidiaSmiLogger:
    return NvidiaSmiLogger(output_csv_path, interval_sec=interval_sec)

