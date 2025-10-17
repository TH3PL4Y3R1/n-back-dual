#!/usr/bin/env python3
"""Quick local sanity check for sequence constraints.

Generates sequences for N in {1,2,3}, validates basic constraints, and prints
the sequence, target flags, and lure types.

Run: PYTHONPATH=. python scripts/local_sequence_check.py
"""
from __future__ import annotations

import sys
from nback.sequences import generate_sequence, validate_sequence


def check(n_back: int, trials: int = 40) -> None:
    plans = generate_sequence(n_back, trials)
    seq = [p.stimulus for p in plans]
    flags = [p.is_target for p in plans]
    lures = [p.lure_type for p in plans]
    ok, reason = validate_sequence(
        seq, flags, lures,
        n_back=n_back,
        target_rate=0.30,
        tolerance=1,
        max_consec_targets=1,
    )
    print(f"N={n_back} trials={trials} -> valid={ok} ({reason})")
    print("seq:\n", ''.join(seq))
    print("targets:", flags)
    print("lures:   ", lures)


if __name__ == "__main__":
    for n in (1, 2, 3):
        check(n, 40)
    sys.exit(0)
