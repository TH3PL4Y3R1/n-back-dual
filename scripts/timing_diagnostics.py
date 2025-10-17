#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timing diagnostics for PsychoPy on this machine.
- Measures frame intervals and reports dropped/long frames.
- Optional full-screen toggle via CLI.

Usage:
    python scripts/timing_diagnostics.py             # windowed
    python scripts/timing_diagnostics.py --fullscr   # full-screen
"""
from __future__ import annotations

import argparse
from statistics import mean

from psychopy import core, visual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fullscr", action="store_true", help="Run full-screen for maximum timing stability")
    parser.add_argument("--frames", type=int, default=600, help="Number of frames to sample")
    args = parser.parse_args()

    win = visual.Window(size=(1280, 720), fullscr=args.fullscr, units="height", color=[0, 0, 0])
    win.setRecordFrameIntervals(True)

    stim = visual.TextStim(win, text="Timing test...", height=0.06, color=[1, 1, 1])

    # Set a fixed frame loop; draw simple content each frame
    for _ in range(args.frames):
        stim.draw()
        win.flip()

    # Collect frame intervals and stats
    fis = list(getattr(win, "frameIntervals", []))
    try:
        refresh_hz = win.getActualFrameRate(nIdentical=20, nMaxFrames=240, nWarmUpFrames=20, threshold=1)
    except Exception:
        refresh_hz = None

    win.close()
    core.quit()

    if not fis:
        print("No frame intervals recorded.")
        return 1

    target = (1.0 / refresh_hz) if refresh_hz else mean(fis)
    long = [x for x in fis if x > target * 1.25]  # >25% slower than nominal

    print("=== Timing diagnostics ===")
    print(f"Frames sampled: {len(fis)}")
    if refresh_hz:
        print(f"Reported refresh rate: {refresh_hz:.3f} Hz (target frame ≈ {target*1000:.2f} ms)")
    print(f"Mean frame interval: {mean(fis)*1000:.2f} ms")
    print(f"Longest frame: {max(fis)*1000:.2f} ms")
    print(f"Long frames (>125% of target): {len(long)}")
    print("==========================")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
