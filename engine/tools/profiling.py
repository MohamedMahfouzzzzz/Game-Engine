# /**************************************************************************/
# /*  profiling.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional, Tuple

import logging


logger = logging.getLogger(__name__)



@dataclass
class ProfileResult:
    label: str
    elapsed_s: float
    mem_current_kb: int
    mem_peak_kb: int


@contextmanager
def profile_block(label: str, enable_memory: bool = True) -> Iterator[ProfileResult]:
    start = time.perf_counter()
    started_tracemalloc = False
    if enable_memory and not tracemalloc.is_tracing():
        tracemalloc.start()
        started_tracemalloc = True
    try:
        yield ProfileResult(label=label, elapsed_s=0.0, mem_current_kb=0, mem_peak_kb=0)
    finally:
        elapsed = time.perf_counter() - start
        current, peak = (0, 0)
        if enable_memory and tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
        if started_tracemalloc:
            tracemalloc.stop()
        # overwrite yielded object by convention: caller can ignore, we also return via print helper
        result = ProfileResult(
            label=label,
            elapsed_s=elapsed,
            mem_current_kb=int(current / 1024),
            mem_peak_kb=int(peak / 1024),
        )
        print(format_profile(result))


def format_profile(result: ProfileResult) -> str:
    return (
        f"[PROFILE] {result.label} | "
        f"{result.elapsed_s:.4f}s | "
        f"mem={result.mem_current_kb}KB peak={result.mem_peak_kb}KB"
    )

