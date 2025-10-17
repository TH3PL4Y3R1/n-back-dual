#!/usr/bin/env python3
"""Smoke test for two-load N-back task.

Runs tiny sessions for Version A (1→3) and Version B (3→1) with 1 block per load
and a small number of trials, in windowed mode and without practice. It prints
detected load per block, total blocks, and verifies that the switch occurs after
block 1 (since blocks_per_load=1 in this test), and that the saved logs include
both loads.

Note: This is a lightweight harness to validate flow and data integrity.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from glob import glob

ROOT = os.path.dirname(os.path.dirname(__file__))


def run_session(version: str) -> str:
    cmd = [
        sys.executable,
        os.path.join(ROOT, 'nback_task.py'),
        '--participant', f'smoke_{version.lower()}',
        '--version', version,
    '--blocks-per-load', '3',
    '--trials', '5',
        '--no-practice',
        '--windowed',
    ]
    print('Running:', ' '.join(cmd))
    res = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(res.stdout)
    if res.returncode != 0:
        raise SystemExit(f"Session {version} failed with code {res.returncode}")
    # Find latest data file for this participant
    data_dir = os.path.join(ROOT, 'data')
    files = sorted(glob(os.path.join(data_dir, f"nback_smoke_{version.lower()}_*.csv")))
    if not files:
        raise AssertionError(f"No CSV found for smoke_{version.lower()}")
    return files[-1]


def load_meta(csv_path: str) -> dict:
    base = os.path.splitext(os.path.basename(csv_path))[0]
    meta_path = os.path.join(os.path.dirname(csv_path), base + '.meta.json')
    if not os.path.exists(meta_path):
        raise AssertionError(f"Missing meta JSON next to {csv_path}")
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_csv(csv_path: str) -> dict:
    loads = []
    blocks = set()
    block_load_map = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split(',')
        n_back_idx = header.index('n_back')
        block_idx_idx = header.index('block_idx')
        for line in f:
            row = line.strip().split(',')
            if len(row) != len(header):
                continue
            nb = int(row[n_back_idx])
            bi = int(row[block_idx_idx])
            loads.append(nb)
            blocks.add(bi)
            block_load_map.setdefault(bi, nb)
    return {
        'unique_loads': sorted(set(loads)),
        'block_count': len(blocks),
        'block_indices': sorted(blocks),
        'block_load_map': dict(sorted(block_load_map.items())),
    }


def main() -> int:
    # Version A: expect order [1,3]
    a_csv = run_session('A')
    a_meta = load_meta(a_csv)
    a_stats = analyze_csv(a_csv)
    assert a_meta.get('version') == 'A', 'Meta version A mismatch'
    assert a_meta.get('load_order') == [1, 3], f"Unexpected load_order in A: {a_meta.get('load_order')}"
    assert a_meta.get('total_blocks') == 6, 'Total blocks should be 6 (3 per load)'
    assert a_stats['block_count'] == 6, f"Expected 6 blocks, got {a_stats['block_count']}"
    assert a_stats['block_indices'] == [1, 2, 3, 4, 5, 6], f"Unexpected block indices: {a_stats['block_indices']}"
    assert 1 in a_stats['unique_loads'] and 3 in a_stats['unique_loads'], 'Both loads must appear in Version A'
    # Switch after block 3
    blm_a = a_stats['block_load_map']
    assert all(blm_a[b] == 1 for b in (1, 2, 3)) and all(blm_a[b] == 3 for b in (4, 5, 6)), 'Version A load order per block incorrect'

    # Version B: expect order [3,1]
    b_csv = run_session('B')
    b_meta = load_meta(b_csv)
    b_stats = analyze_csv(b_csv)
    assert b_meta.get('version') == 'B', 'Meta version B mismatch'
    assert b_meta.get('load_order') == [3, 1], f"Unexpected load_order in B: {b_meta.get('load_order')}"
    assert b_meta.get('total_blocks') == 6, 'Total blocks should be 6 (3 per load)'
    assert b_stats['block_count'] == 6, f"Expected 6 blocks, got {b_stats['block_count']}"
    assert b_stats['block_indices'] == [1, 2, 3, 4, 5, 6], f"Unexpected block indices: {b_stats['block_indices']}"
    assert 1 in b_stats['unique_loads'] and 3 in b_stats['unique_loads'], 'Both loads must appear in Version B'
    # Switch after block 3
    blm_b = b_stats['block_load_map']
    assert all(blm_b[b] == 3 for b in (1, 2, 3)) and all(blm_b[b] == 1 for b in (4, 5, 6)), 'Version B load order per block incorrect'

    print('Smoke test passed.')
    print('A CSV:', a_csv)
    print('A block loads:', a_stats['block_load_map'])
    print('B CSV:', b_csv)
    print('B block loads:', b_stats['block_load_map'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
