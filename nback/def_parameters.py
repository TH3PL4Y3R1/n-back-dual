"""Default parameters and constants for the N-back task.

Separated from the main task file to keep things tidy and reusable.
"""

from __future__ import annotations

import string

# Task structure
BLOCKS_PER_LOAD_DEFAULT = 3
TRIALS_PER_BLOCK = 60

# Practice
PRACTICE_TRIALS = 30
PRACTICE_TARGET_RATE = 0.40
PRACTICE_HAS_LURES = False
PRACTICE_PASS_ACC = 0.75

# Stimulus set
EXCLUDE_CONFUSABLES = True  # Exclude I/O/Q if True
LETTERS = [c for c in string.ascii_uppercase]
if EXCLUDE_CONFUSABLES:
    LETTERS = [c for c in LETTERS if c not in {"I", "O", "Q"}]

# Timing (ms)
FIXATION_DUR_MS = 500
STIM_DUR_MS = 500
SOA_MS_DEFAULT = 2500  # constant stimulus onset asynchrony (ms)

# Sequence constraints (defaults used when building blocks)
TARGET_RATE = 0.30
LURE_N_MINUS_1_RATE = 0.05
LURE_N_PLUS_1_RATE = 0.05

# Default limit on consecutive targets
MAX_CONSEC_TARGETS_DEFAULT = 1

# Visuals
BACKGROUND_COLOR = [0.2, 0.2, 0.2]  # gray
TEXT_COLOR = [1.0, 1.0, 1.0]
FONT = "Arial"
FONT_HEIGHT = 0.12  # normalized units
FIXATION_HEIGHT = 0.18

# Keys
KEY_PROCEED = "return"
KEY_RESPONSE = "space"
KEY_QUIT = "escape"

__all__ = [
    # structure
    "BLOCKS_PER_LOAD_DEFAULT",
    "TRIALS_PER_BLOCK",
    # practice
    "PRACTICE_TRIALS",
    "PRACTICE_TARGET_RATE",
    "PRACTICE_HAS_LURES",
    "PRACTICE_PASS_ACC",
    # letters
    "EXCLUDE_CONFUSABLES",
    "LETTERS",
    # timing/soa
    "FIXATION_DUR_MS",
    "STIM_DUR_MS",
    "SOA_MS_DEFAULT",
    # sequence constraints
    "TARGET_RATE",
    "LURE_N_MINUS_1_RATE",
    "LURE_N_PLUS_1_RATE",
    "MAX_CONSEC_TARGETS_DEFAULT",
    # visuals
    "BACKGROUND_COLOR",
    "TEXT_COLOR",
    "FONT",
    "FONT_HEIGHT",
    "FIXATION_HEIGHT",
    # keys
    "KEY_PROCEED",
    "KEY_RESPONSE",
    "KEY_QUIT",
]
