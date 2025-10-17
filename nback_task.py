#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PsychoPy N-back task with optional (commented) marker plumbing for EEG/ECG integrations.
- Runs out of the box with markers disabled (no-op).
- Toggle ENABLE_MARKERS to True and follow commented examples to integrate with LSL/Serial/Parallel.

Refactor: Each session now runs two sequential N-back loads (Version A: 1→3, Version B: 3→1).
Structure: Consent → Instructions → Practice (always 2-back) → Main task
          (3 blocks of first load + 3 blocks of second load) → Thanks → Save/Exit

Data: Writes trial-wise CSV to ./data/nback_{participantID}_{YYYYMMDD_HHMMSS}.csv
"""

from __future__ import annotations

import os
import sys
import csv
import random
import argparse
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from psychopy import core, visual, event
try:
    from psychopy.hardware import keyboard as hw_keyboard
    _HAVE_HW_KB = True
except Exception:
    _HAVE_HW_KB = False
from nback.markers import (
    set_enable,
    create_parallel_port,
    send_named,
    TRIGGERS,
)
from nback.sequences import (TrialPlan, generate_sequence)
from nback.def_parameters import (
    BLOCKS_PER_LOAD_DEFAULT,
    TRIALS_PER_BLOCK,
    PRACTICE_TRIALS,
    PRACTICE_TARGET_RATE,
    PRACTICE_HAS_LURES,
    PRACTICE_PASS_ACC,
    EXCLUDE_CONFUSABLES,
    LETTERS,
    FIXATION_DUR_MS,
    STIM_DUR_MS,
    SOA_MS_DEFAULT,
    TARGET_RATE,
    LURE_N_MINUS_1_RATE,
    LURE_N_PLUS_1_RATE,
    MAX_CONSEC_TARGETS_DEFAULT,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    FONT,
    FONT_HEIGHT,
    FIXATION_HEIGHT,
    KEY_PROCEED,
    KEY_RESPONSE,
    KEY_QUIT,
)
from nback.utilities import (
    make_data_dir as util_make_data_dir,
    timestamp as util_timestamp,
    safe_filename as util_safe_filename,
    _default_wrap_width as util_default_wrap_width,
    make_autosized_text as util_make_autosized_text,
)

"""Main N-back task entry point.

Implements a fixed-SOA trial structure suitable for EEG/physio:
- Each trial lasts exactly SOA milliseconds from stimulus onset to the next.
- Stimulus is shown for STIM_DUR_MS, then fixation until SOA elapses.
- Responses are accepted throughout the whole SOA window and time-locked to stimulus onset.
- Event markers are emitted at stimulus onset, fixation onset, response, block start/end, and end-of-task.

This file focuses on experiment flow, timing, rendering, and data I/O.
Sequence generation and marker transports live in separate modules.
"""

# =========================
# Parameters (defaults)
# =========================
# Task structure
# Practice is fixed at 2-back; main task runs two sequential N-back loads.
BLOCKS_PER_LOAD_DEFAULT = 3
TRIALS_PER_BLOCK = 60

# Practice
PRACTICE_TRIALS = 30   # default; can be overridden via --practice-trials
PRACTICE_TARGET_RATE = 0.40
PRACTICE_HAS_LURES = False
# Practice passing criterion (fraction correct)
PRACTICE_PASS_ACC = 0.75

# Stimulus set
EXCLUDE_CONFUSABLES = EXCLUDE_CONFUSABLES
LETTERS = LETTERS

# Timing (ms)
FIXATION_DUR_MS = FIXATION_DUR_MS
STIM_DUR_MS = STIM_DUR_MS
SOA_MS_DEFAULT = SOA_MS_DEFAULT

# Sequence constraints (defaults used when building blocks)
TARGET_RATE = TARGET_RATE
LURE_N_MINUS_1_RATE = LURE_N_MINUS_1_RATE
LURE_N_PLUS_1_RATE = LURE_N_PLUS_1_RATE

# Default limit on consecutive targets (can be overridden via CLI)
MAX_CONSEC_TARGETS_DEFAULT = MAX_CONSEC_TARGETS_DEFAULT

# Visuals
BACKGROUND_COLOR = BACKGROUND_COLOR
TEXT_COLOR = TEXT_COLOR
FONT = FONT
FONT_HEIGHT = FONT_HEIGHT
FIXATION_HEIGHT = FIXATION_HEIGHT

# Keys
KEY_PROCEED = KEY_PROCEED
KEY_RESPONSE = KEY_RESPONSE
KEY_QUIT = KEY_QUIT

"""Markers are imported from nback.markers (Bosch-compatible)."""

# Hardware marker state (set in main)
GLOBAL_PARALLEL_PORT = None  # type: ignore
GLOBAL_EYELINK = None        # type: ignore

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEXTS_DIR = os.path.join(os.path.dirname(__file__), "texts")
CONSENT_FILE = os.path.join(TEXTS_DIR, "informed_consent.txt")

# Runtime configuration (set from CLI in main())
CFG_TARGET_RATE = TARGET_RATE
CFG_LURE_NM1 = LURE_N_MINUS_1_RATE
CFG_LURE_NP1 = LURE_N_PLUS_1_RATE
CFG_MAX_CONSEC_TARGETS = MAX_CONSEC_TARGETS_DEFAULT
CFG_SOA_MS = SOA_MS_DEFAULT
# ITI for logging/sequence plan is the remainder of SOA after stimulus visibility
CFG_FIXED_ITI_MS = max(0, SOA_MS_DEFAULT - STIM_DUR_MS)
CFG_USE_HW_KB = True  # toggled by --kb-backend

# Pre-created stimuli (initialized after window creation)
STIM_LETTER: Optional[visual.TextStim] = None
STIM_FIXATION: Optional[visual.TextStim] = None


# =========================
# Utilities
# =========================

def make_data_dir(path: str = DATA_DIR) -> None:
    util_make_data_dir(path)


def timestamp() -> str:
    return util_timestamp()


def safe_filename(name: str) -> str:
    return util_safe_filename(name)


# =========================
"""Marker plumbing lives in nback/markers.py; send_marker is imported."""


# =========================
# Sequence generation
# =========================

"""TrialPlan dataclass and sequence generation helpers are in nback.sequences."""


# Sequence creation is delegated to nback.sequences.generate_sequence


# =========================
# Rendering / Task flow
# =========================

def show_consent(win: visual.Window, text_stim: Optional[visual.TextStim] = None, consent_file: Optional[str] = None) -> None:
    """Show informed consent first.
    Loads text from informed_consent.txt and appends "(Press ENTER to continue)".
    ENTER proceeds; ESC quits (no save).
    The consent marker call is present but commented by default.
    """
    # Load consent text from file (UTF-8). Fallback to minimal notice if missing.
    path = consent_file or CONSENT_FILE
    consent_text = None
    try:
        with open(path, "r", encoding="utf-8") as cf:
            consent_text = cf.read().strip()
    except Exception:
        consent_text = None

    if not consent_text:
        consent_text = (
            "Consent text file not found. Please add informed_consent.txt next to nback_task.py."
        )
    # Auto-scale to fit window height (avoids text running off-screen on smaller displays)
    txt = f"{consent_text}\n\n(Press ENTER to continue)"

    if text_stim is None:
        stim = _make_autosized_text(win, txt, align='left')
    else:
        # If a custom stim supplied, still ensure appended prompt and wrapping
        text_stim.text = txt
        text_stim.wrapWidth = text_stim.wrapWidth or _default_wrap_width(win)
        stim = text_stim

    stim.draw()
    win.flip()
    # Bosch-compatible marker: consent shown when displayed
    try:
        send_named('consent_shown', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break


INSTR_WELCOME_FILE = os.path.join(TEXTS_DIR, "instructions_welcome.txt")
INSTR_PRACTICE_FILE = os.path.join(TEXTS_DIR, "instructions_practice_headsup.txt")
INSTR_TASK_FILE = os.path.join(TEXTS_DIR, "instructions_task_headsup.txt")
INSTR_BREAK_FILE = os.path.join(TEXTS_DIR, "instructions_break.txt")
INSTR_THANKS_FILE = os.path.join(TEXTS_DIR, "instructions_thanks.txt")
INSTR_SAVE_EXIT_FILE = os.path.join(TEXTS_DIR, "instructions_save_and_exit.txt")
INSTR_PRACTICE_PASS_FILE = os.path.join(TEXTS_DIR, "instructions_practice_feedback_pass.txt")
INSTR_PRACTICE_FAIL_FILE = os.path.join(TEXTS_DIR, "instructions_practice_feedback_fail.txt")
INSTR_PHASE_1BACK_FILE = os.path.join(TEXTS_DIR, "instructions_phase_1back.txt")
INSTR_PHASE_2BACK_FILE = os.path.join(TEXTS_DIR, "instructions_phase_2back.txt")
INSTR_PHASE_3BACK_FILE = os.path.join(TEXTS_DIR, "instructions_phase_3back.txt")


def _load_text(path: str, fallback: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            return txt if txt else fallback
    except Exception:
        return fallback


def show_instructions_multi(win: visual.Window, load_order: List[int]) -> None:
    """Session instructions for the two-load design.

    Displays a welcome message and explicitly states the practice and the two
    N-back loads that will follow (e.g., 1-back then 3-back).
    """
    base = _load_text(INSTR_WELCOME_FILE, "Welcome to the N-back task.\nPress ENTER/RETURN to begin practice.")
    seq_txt = f"This session includes two difficulty levels: {load_order[0]}-back followed by {load_order[1]}-back.\nPractice will always be 2-back."
    txt = base.replace("{{N}}", "N").strip() + f"\n\n{seq_txt}\n\n(Press ENTER/RETURN to continue)"
    stim = _make_autosized_text(win, txt, align='center')
    stim.draw(); win.flip()
    # Mark instructions shown when displayed
    try:
        send_named('instructions_shown', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break


# =========================
# Text auto-sizing utilities
# =========================

def _default_wrap_width(win: visual.Window, margin: float = 0.95) -> float:
    return util_default_wrap_width(win, margin)


def _make_autosized_text(
    win: visual.Window,
    text: str,
    start_height: float = 0.07,
    min_height: float = 0.03,
    max_height_frac: float = 0.9,
    shrink_factor: float = 0.9,
    align: str = 'left',
) -> visual.TextStim:
    return util_make_autosized_text(win, text, start_height, min_height, max_height_frac, shrink_factor, align, color=TEXT_COLOR, font=FONT)


def show_practice_headsup(win: visual.Window) -> None:
    """Show a brief screen before starting practice; waits for ENTER or ESC."""
    msg = _load_text(INSTR_PRACTICE_FILE, "Practice is about to begin. Try to reach the accuracy criterion to proceed.") + "\n\n(Press ENTER/RETURN to start)"
    stim = _make_autosized_text(win, msg, align='center')
    stim.draw(); win.flip()
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break


def show_break(win: visual.Window, block_idx: int, acc: float, mean_rt: Optional[float]) -> None:
    """Show between-block break with simple performance feedback."""
    template = _load_text(INSTR_BREAK_FILE, "End of block {{BLOCK}}. Accuracy: {{ACC}}%\n")
    body = template.replace("{{BLOCK}}", str(block_idx)).replace("{{ACC}}", f"{acc*100:.1f}")
    if mean_rt is not None:
        body += f"Mean RT (correct): {mean_rt:.0f} ms\n"
    body += "\nPress ENTER/RETURN to continue."
    stim = _make_autosized_text(win, body, align='center')
    stim.draw(); win.flip()
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break


def show_thanks(win: visual.Window) -> None:
    """Display final thank-you screen and emit completion marker."""
    text = _load_text(INSTR_THANKS_FILE, "Thank you!") + "\n"
    stim = _make_autosized_text(win, text, start_height=0.09, align='center')
    stim.draw(); win.flip()
    try:
        send_named('debrief_shown', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass
    core.wait(1.5)


def show_save_and_exit_prompt(win: visual.Window) -> None:
    """Final screen requiring ENTER/RETURN to save and exit; ESC ignored here."""
    msg = _load_text(INSTR_SAVE_EXIT_FILE, "Task complete. Press ENTER/RETURN to save and exit.")
    stim = _make_autosized_text(win, msg + "\n", align='center')
    stim.draw(); win.flip()
    event.clearEvents()
    # Only accept ENTER here; ignore ESC
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED])
        if KEY_PROCEED in keys:
            break


def run_practice(win: visual.Window, n_back: int, practice_trials: int) -> Tuple[float, Optional[float]]:
    """Run a practice block and provide pass/fail feedback.

    Returns:
    - acc: fraction correct over practice trials
    - mean_rt: mean RT (ms) on correct trials, or None if no correct responses
    Timing: identical to the main task (fixed SOA, stimulus then fixation).
    """
    plans = generate_sequence(
        n_back,
        practice_trials,
        target_rate=PRACTICE_TARGET_RATE,
        lure_n_minus_1_rate=CFG_LURE_NM1 if PRACTICE_HAS_LURES else 0.0,
        lure_n_plus_1_rate=CFG_LURE_NP1 if PRACTICE_HAS_LURES else 0.0,
        max_consec_targets=CFG_MAX_CONSEC_TARGETS,
        fixed_iti_ms=CFG_FIXED_ITI_MS,
        include_lures=PRACTICE_HAS_LURES,
    )
    accs: List[int] = []
    rts: List[float] = []
    _ = run_block(win, block_idx=0, n_back=n_back, plans=plans, is_practice=True,
                  accs_out=accs, rts_out=rts, rows_out=None)
    acc = sum(accs) / len(accs) if accs else 0.0
    mean_rt = (sum(rts) / len(rts)) if rts else None

    # Feedback
    passed = acc >= PRACTICE_PASS_ACC
    if passed:
        template = _load_text(INSTR_PRACTICE_PASS_FILE, "Practice complete. Accuracy: {{ACC}}% (criterion: {{CRIT}}%).\nYou passed the criterion. Press ENTER/RETURN to continue.")
    else:
        template = _load_text(INSTR_PRACTICE_FAIL_FILE, "Practice complete. Accuracy: {{ACC}}% (criterion: {{CRIT}}%).\nYou did not reach the criterion. Press ENTER/RETURN to repeat practice.")
    msg = template.replace("{{ACC}}", f"{acc*100:.1f}").replace("{{CRIT}}", f"{PRACTICE_PASS_ACC*100:.0f}")
    if mean_rt is not None:
        msg += f"\nMean RT (correct): {mean_rt:.0f} ms"
    stim = _make_autosized_text(win, msg, align='center')
    stim.draw(); win.flip()
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break
    return acc, mean_rt


def show_task_headsup(win: visual.Window, n_back: int) -> None:
    """Heads-up screen before a main-task phase; waits for ENTER or ESC."""
    base = _load_text(INSTR_TASK_FILE, "Main task is about to begin. Press ENTER/RETURN to start the task.")
    txt = base.replace("{{N}}", str(n_back)) + "\n\n(Press ENTER/RETURN to start the task)"
    stim = _make_autosized_text(win, txt, align='center')
    stim.draw(); win.flip()
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break


def show_phase_instructions(win: visual.Window, n_back: int) -> None:
    """Show phase-specific instructions from a per-N text file when present.

    Looks for `texts/instructions_phase_{n}back.txt`. If not found, falls back
    to the generic `instructions_task_headsup.txt`. Replaces `{{N}}` with the
    numeric N value. Requires ENTER/RETURN to proceed; ESC quits.
    """
    path_map = {
        1: INSTR_PHASE_1BACK_FILE,
        2: INSTR_PHASE_2BACK_FILE,
        3: INSTR_PHASE_3BACK_FILE,
    }
    path = path_map.get(int(n_back), INSTR_TASK_FILE)
    if os.path.exists(path):
        base = _load_text(path, f"You are about to start the {n_back}-back phase.")
    else:
        base = _load_text(INSTR_TASK_FILE, "Main task is about to begin.")
    txt = base.replace("{{N}}", str(n_back)).strip()
    if "Press ENTER" not in txt and "ENTER/RETURN" not in txt:
        txt += "\n\n(Press ENTER/RETURN to start)"
    stim = _make_autosized_text(win, txt, align='center')
    stim.draw(); win.flip()
    event.clearEvents()
    while True:
        keys = event.waitKeys(keyList=[KEY_PROCEED, KEY_QUIT])
        if KEY_QUIT in keys:
            graceful_quit(None, None, [], win, abort=True)
        if KEY_PROCEED in keys:
            break


def _ensure_stims(win: visual.Window) -> None:
    """Create shared TextStim objects for stimulus and fixation if missing."""
    global STIM_LETTER, STIM_FIXATION
    if STIM_LETTER is None:
        STIM_LETTER = visual.TextStim(win, text="", color=TEXT_COLOR, font=FONT, height=FONT_HEIGHT)
    if STIM_FIXATION is None:
        STIM_FIXATION = visual.TextStim(win, text="+", color=TEXT_COLOR, font=FONT, height=FIXATION_HEIGHT)


def _draw_fixation(win: visual.Window) -> None:
    """Draw fixation (+) using a prebuilt TextStim (does not flip)."""
    _ensure_stims(win)
    assert STIM_FIXATION is not None
    STIM_FIXATION.draw()


def _draw_stimulus(win: visual.Window, letter: str) -> None:
    """Draw the letter stimulus using a prebuilt TextStim (does not flip)."""
    _ensure_stims(win)
    assert STIM_LETTER is not None
    STIM_LETTER.text = letter
    STIM_LETTER.draw()


# Note: fixed-SOA pacing is implemented in run_block; no generic flip-for-ms helper needed.


def _marker_code_for_stim(is_target: int, lure_type: str) -> int:
    # Keep a code for CSV; this no longer controls hardware sends directly
    if is_target:
        return 41  # legacy: target
    if lure_type == "n-1":
        return 43
    if lure_type == "n+1":
        return 44
    return 42


def run_block(win: visual.Window, block_idx: int, n_back: int, plans: List[TrialPlan],
              is_practice: bool, accs_out: List[int], rts_out: List[float],
              rows_out: Optional[List[Dict]]) -> Tuple[float, Optional[float]]:
    """Run a single block of trials using fixed-SOA pacing.

    Behavior:
    - Each trial starts with stimulus onset (flip). Marker aligns to this flip.
    - Stimulus shown for STIM_DUR_MS, then fixation until SOA.
    - Responses collected from onset until SOA elapses (next trial onset).

    Returns:
    - block accuracy and mean RT (ms) for correct trials in this block.
    """
    # Start marker (by load)
    try:
        send_named('block_ll_start' if n_back == 1 else 'block_hl_start',
                   parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass

    # Use hardware keyboard when available for better timing
    kb = None
    if CFG_USE_HW_KB and _HAVE_HW_KB:
        try:
            kb = hw_keyboard.Keyboard(clock=core.Clock())
        except Exception:
            kb = None

    # Trial loop
    correct_count = 0

    for t_idx, plan in enumerate(plans, start=1):
        # Stimulus onset
        _draw_stimulus(win, plan.stimulus)
        # Prepare response clock aligned with the stimulus flip
        resp_clock = core.Clock()
        win.callOnFlip(resp_clock.reset)
        if CFG_USE_HW_KB and _HAVE_HW_KB and kb is not None:
            kb.clock = resp_clock
            kb.clearEvents()
        stim_onset = win.flip()
        stim_marker = _marker_code_for_stim(plan.is_target, plan.lure_type)
        try:
            send_named('stim_presentation', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
        except Exception:
            pass

        # Response collection
        got_response = False
        resp_key = None
        rt_ms: Optional[float] = None

        # Present for STIM_DUR_MS, then fixation until SOA; accept responses until SOA
        fixation_mark_sent = False
        while True:
            now_ms = resp_clock.getTime() * 1000.0
            if now_ms >= CFG_SOA_MS:
                break
            if CFG_USE_HW_KB and _HAVE_HW_KB and kb is not None:
                keys = kb.getKeys(keyList=[KEY_RESPONSE, KEY_QUIT], waitRelease=False, clear=False)
                if keys and not got_response:
                    k = keys[0]
                    name = k.name
                    if name == KEY_QUIT:
                        graceful_quit(None, None, rows_out if rows_out is not None else [], win, abort=True)
                    got_response = True
                    resp_key = name
                    rt_ms = (k.rt or 0.0) * 1000.0
                    try:
                        send_named('response_ll' if n_back == 1 else 'response_hl',
                                   parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
                    except Exception:
                        pass
            else:
                keys = event.getKeys(keyList=[KEY_RESPONSE, KEY_QUIT], timeStamped=resp_clock)
                if keys and not got_response:
                    for k, t in keys:
                        if k == KEY_QUIT:
                            graceful_quit(None, None, rows_out if rows_out is not None else [], win, abort=True)
                        if k:
                            got_response = True
                            resp_key = k
                            rt_ms = t * 1000.0
                            try:
                                send_named('response_ll' if n_back == 1 else 'response_hl',
                                           parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
                            except Exception:
                                pass
                            break
            # Draw based on phase: stimulus then fixation
            if now_ms < STIM_DUR_MS:
                _draw_stimulus(win, plan.stimulus)
            else:
                if not fixation_mark_sent:
                    try:
                        send_named('fixation_onset', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
                    except Exception:
                        pass
                    fixation_mark_sent = True
                _draw_fixation(win)
            win.flip()

        # Score
        is_space = (resp_key == KEY_RESPONSE)
        correct = int((plan.is_target == 1 and is_space) or (plan.is_target == 0 and not is_space))
        if correct:
            correct_count += 1
        accs_out.append(correct)
        if correct and rt_ms is not None:
            rts_out.append(rt_ms)

        # Row output
        if rows_out is not None:
            row = {
                "participant_id": CURRENT_PARTICIPANT,
                "session_timestamp": SESSION_TS,
                "block_idx": block_idx,
                "trial_idx": t_idx,
                "n_back": n_back,
                "stimulus": plan.stimulus,
                "is_target": plan.is_target,
                "lure_type": plan.lure_type,
                "iti_ms": plan.iti_ms,
                "stim_onset_time": f"{stim_onset:.6f}",
                "response_key": resp_key or "",
                "rt_ms": f"{rt_ms:.2f}" if rt_ms is not None else "",
                "correct": correct,
                "marker_code_stim": stim_marker,
                "marker_code_resp": (50 if n_back == 1 else 51) if got_response else "",
            }
            rows_out.append(row)

    # No trailing ITI; pacing is enforced per-trial via SOA

    # End marker (by load)
    try:
        send_named('block_ll_end' if n_back == 1 else 'block_hl_end',
                   parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass

    acc = correct_count / len(plans) if plans else 0.0
    mean_rt = (sum(rts_out) / len(rts_out)) if rts_out else None
    return acc, mean_rt


# =========================
# Graceful quit and CSV
# =========================

CURRENT_PARTICIPANT = ""
SESSION_TS = ""
CSV_PATH = ""
ABORT_WITHOUT_SAVE = False
META_PATH = ""


def graceful_quit(writer: Optional[csv.DictWriter], f: Optional[object], rows: List[Dict], win: Optional[visual.Window], abort: bool = False) -> None:
    """Close the task cleanly, saving rows unless aborting.

    If abort is True (e.g., ESC pressed), delete any partially written files and
    suppress saving remaining rows. Always attempts to close the PsychoPy window.
    """
    global ABORT_WITHOUT_SAVE
    ABORT_WITHOUT_SAVE = ABORT_WITHOUT_SAVE or abort

    # Only save when not aborting
    if not ABORT_WITHOUT_SAVE:
        try:
            if writer is not None and f is not None and rows:
                writer.writerows(rows)
                f.flush()
        except Exception:
            pass
    # Close file handle if present
    try:
        if f is not None:
            f.close()
    except Exception:
        pass
    # If aborting, remove CSV/metadata files if they exist
    if ABORT_WITHOUT_SAVE:
        try:
            if CSV_PATH and os.path.exists(CSV_PATH):
                os.remove(CSV_PATH)
        except Exception:
            pass
        try:
            if META_PATH and os.path.exists(META_PATH):
                os.remove(META_PATH)
        except Exception:
            pass
    # Close window
    try:
        if win is not None:
            win.close()
    except Exception:
        pass
    core.quit()


# =========================
# Main
# =========================

def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry-point for running the N-back task.

    Flow:
    - Parse CLI, configure timing (fixed SOA), input backend, and display.
    - Consent → Instructions → Practice (optional) → Heads-up → Blocks → Thanks → Save/Exit.
    - Writes per-trial CSV and a metadata JSON sidecar.
    """
    global CURRENT_PARTICIPANT, SESSION_TS, CSV_PATH, META_PATH

    parser = argparse.ArgumentParser(description="PsychoPy N-back Task (two-load version)")
    parser.add_argument("--participant", "-p", default="anon", help="Participant ID")
    # Two version orders: A = 1-back then 3-back; B = 3-back then 1-back
    parser.add_argument("--version", choices=["A", "B"], default="A", help="Load order: A=1→3, B=3→1")
    parser.add_argument("--blocks-per-load", type=int, default=BLOCKS_PER_LOAD_DEFAULT, help="Blocks per load (default: 3)")
    parser.add_argument("--trials", type=int, default=TRIALS_PER_BLOCK, help="Trials per block")
    parser.add_argument("--no-practice", action="store_true", help="Skip practice")
    parser.add_argument("--practice-trials", type=int, default=PRACTICE_TRIALS, help="Number of practice trials")
    # Fixed SOA timing (legacy ITI jitter removed)
    parser.add_argument("--lure-nminus1", type=float, default=LURE_N_MINUS_1_RATE, help="Probability of n-1 lures per non-target trial")
    parser.add_argument("--lure-nplus1", type=float, default=LURE_N_PLUS_1_RATE, help="Probability of n+1 lures per non-target trial")
    parser.add_argument("--target-rate", type=float, default=TARGET_RATE, help="Target rate (0-1) per block")
    parser.add_argument("--max-consec-targets", type=int, default=MAX_CONSEC_TARGETS_DEFAULT, help="Maximum allowed consecutive targets")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    # Default to full-screen; allow windowed mode for debugging
    parser.add_argument("--windowed", action="store_true", help="Run windowed for debugging (default: fullscreen)")
    parser.add_argument("--screen", type=int, default=None, help="Display/screen index (0=primary). If unset, PsychoPy default is used.")
    parser.add_argument("--list-screens", action="store_true", help="List detected screens and exit.")
    parser.add_argument("--kb-backend", choices=["ptb", "event"], default="event", help="Keyboard backend: 'ptb' (hardware; low-latency) or 'event' (fallback)")
    parser.add_argument("--soa-ms", type=int, default=SOA_MS_DEFAULT, help="Constant stimulus onset asynchrony (ms). Default: 2500")
    # If legacy single-load flags are present in argv, fail with guidance
    if argv is None:
        argv_check = sys.argv[1:]
    else:
        argv_check = list(argv)
    if any(arg.startswith("--n-back") for arg in argv_check) or any(arg == "--blocks" for arg in argv_check) or any(arg.startswith("--blocks=") for arg in argv_check):
        raise SystemExit("Legacy flags detected (--n-back/--blocks). This task now requires --version {A|B} and --blocks-per-load. Example: --version A --blocks-per-load 3")

    args = parser.parse_args(argv)

    # Optional screen enumeration (no window creation yet)
    if args.list_screens:
        print("Listing available physical screens (indices for --screen):")
        try:
            try:
                import pyglet  # type: ignore
                display = pyglet.canvas.get_display()
                screens = display.get_screens()
                for idx, s in enumerate(screens):
                    # Some backends expose x/y; guard with getattr
                    pos = f"@({getattr(s, 'x', '?')},{getattr(s, 'y', '?')})"
                    print(f"  [{idx}] {s.width}x{s.height} {pos}")
            except Exception as e:
                print(f"  (pyglet enumeration failed: {e})")
            # Also list any named monitor profiles (Psychopy Monitor Center)
            try:
                from psychopy import monitors  # type: ignore
                profs = monitors.getAllMonitors()
                if profs:
                    print("Monitor profiles (Monitor Center names):")
                    for name in profs:
                        mon = monitors.Monitor(name)
                        size = mon.getSizePix()
                        dist = mon.getDistance()
                        width = mon.getWidth()
                        meta_bits = []
                        if size:
                            meta_bits.append(f"res={size[0]}x{size[1]}")
                        if dist:
                            meta_bits.append(f"dist={dist}cm")
                        if width:
                            meta_bits.append(f"width={width}cm")
                        meta = ", ".join(meta_bits)
                        print(f"  - {name}: {meta}")
            except Exception:
                pass
        finally:
            print("Done. Use --screen INDEX to select a screen.")
        return 0

    # Determine load order from --version flag
    load_order = [1, 3] if args.version == "A" else [3, 1]
    blocks_per_load = max(1, int(args.blocks_per_load))
    trials_per_block = int(args.trials)
    CURRENT_PARTICIPANT = safe_filename(str(args.participant)) or "anon"
    SESSION_TS = timestamp()

    # Configure RNG
    if args.seed is not None:
        random.seed(int(args.seed))

    # Apply CLI config
    global CFG_TARGET_RATE, CFG_LURE_NM1, CFG_LURE_NP1, CFG_MAX_CONSEC_TARGETS, CFG_SOA_MS, CFG_FIXED_ITI_MS
    CFG_TARGET_RATE = float(max(0.0, min(1.0, args.target_rate)))
    CFG_LURE_NM1 = float(max(0.0, min(1.0, args.lure_nminus1)))
    CFG_LURE_NP1 = float(max(0.0, min(1.0, args.lure_nplus1)))
    CFG_MAX_CONSEC_TARGETS = max(1, int(args.max_consec_targets))
    # Fixed SOA: ITI = SOA - STIM_DUR_MS; response window extends until next onset
    CFG_SOA_MS = max(1, int(args.soa_ms))
    CFG_FIXED_ITI_MS = max(0, CFG_SOA_MS - STIM_DUR_MS)
    # Keyboard backend selection
    global CFG_USE_HW_KB
    CFG_USE_HW_KB = (args.kb_backend == "ptb") and _HAVE_HW_KB
    if args.kb_backend == "ptb" and not _HAVE_HW_KB:
        print("Note: psychtoolbox keyboard backend unavailable; falling back to 'event' backend.")

    make_data_dir(DATA_DIR)
    csv_name = f"nback_{CURRENT_PARTICIPANT}_{SESSION_TS}.csv"
    CSV_PATH = os.path.join(DATA_DIR, csv_name)
    META_PATH = os.path.join(DATA_DIR, f"nback_{CURRENT_PARTICIPANT}_{SESSION_TS}.meta.json")

    # Configure window
    fullscr = not bool(args.windowed)
    win_kwargs = dict(size=(1280, 720), color=BACKGROUND_COLOR, units="height", fullscr=fullscr, allowGUI=False)
    if args.screen is not None:
        # PsychoPy uses pyglet screen indices; user supplies int
        win_kwargs["screen"] = int(args.screen)
    win = visual.Window(**win_kwargs)
    try:
        win.mouseVisible = False
    except Exception:
        pass
    # Ensure frame-syncing
    try:
        win.waitBlanking = True
    except Exception:
        pass

    # Detect and report display refresh rate
    refresh_hz = None
    try:
        refresh_hz = win.getActualFrameRate(nIdentical=20, nMaxFrames=240, nWarmUpFrames=20, threshold=1)
    except Exception:
        refresh_hz = None
    if refresh_hz:
        print(f"Detected display refresh: {refresh_hz:.3f} Hz (frame ≈ {1000.0/refresh_hz:.2f} ms)")
    else:
        print("Warning: Could not detect display refresh rate; proceeding without it.")

    # =========================
    # Hardware markers: safe initialization (works without hardware)
    # =========================
    global GLOBAL_PARALLEL_PORT, GLOBAL_EYELINK
    GLOBAL_PARALLEL_PORT = None
    GLOBAL_EYELINK = None
    try:
        # Bosch default address
        GLOBAL_PARALLEL_PORT = create_parallel_port(0x03BC)
        set_enable(True)
    except Exception:
        GLOBAL_PARALLEL_PORT = None
        set_enable(False)
    # EyeLink is optional; only wire if your session sets it up elsewhere
    try:
        import pylink  # type: ignore
        # If you have a session-wide EyeLink object, assign it like:
        # GLOBAL_EYELINK = existing_eyelink_instance
        GLOBAL_EYELINK = None
    except Exception:
        GLOBAL_EYELINK = None

    # Mark experiment start
    try:
        send_named('experiment_start', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass

    # =========================
    # PHASE: Consent -> Instructions -> Practice heads-up
    # =========================
    show_consent(win)
    show_instructions_multi(win, load_order)
    show_practice_headsup(win)

    # Prepare CSV
    fieldnames = [
        "participant_id", "session_timestamp", "block_idx", "trial_idx",
        "n_back", "stimulus", "is_target", "lure_type", "iti_ms",
        "stim_onset_time", "response_key", "rt_ms", "correct",
        "marker_code_stim", "marker_code_resp",
    ]

    f = open(CSV_PATH, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    # Write sidecar metadata JSON for reproducibility (includes display refresh and fullscreen)
    try:
        meta = {
            "participant_id": CURRENT_PARTICIPANT,
            "session_timestamp": SESSION_TS,
            "practice_n_back": 2,
            "version": args.version,
            "load_order": load_order,
            "blocks_per_load": blocks_per_load,
            "total_blocks": 2 * blocks_per_load,
            "trials_per_block": trials_per_block,
            "practice_trials": int(args.practice_trials),
            "practice_target_rate": PRACTICE_TARGET_RATE,
            "practice_has_lures": PRACTICE_HAS_LURES,
            "target_rate": CFG_TARGET_RATE,
            "lure_nminus1_rate": CFG_LURE_NM1,
            "lure_nplus1_rate": CFG_LURE_NP1,
            "max_consec_targets": CFG_MAX_CONSEC_TARGETS,
            # constant SOA model; per-trial iti_ms equals (soa_ms - stim_dur_ms)
            "seed": args.seed,
            "letters": LETTERS,
            "psychopy_version": None,
            "display_refresh_hz": refresh_hz,
            "window_fullscreen": bool(fullscr),
            "screen_index": args.screen,
            "soa_ms": CFG_SOA_MS,
            "fixed_iti_ms": CFG_FIXED_ITI_MS,
            "kb_backend": "ptb" if (CFG_USE_HW_KB and _HAVE_HW_KB) else "event",
        }
        try:
            import psychopy
            meta["psychopy_version"] = getattr(psychopy, "__version__", None)
        except Exception:
            pass
        with open(META_PATH, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2)
    except Exception:
        pass

    all_rows: List[Dict] = []
    overall_accs: List[int] = []
    overall_rts: List[float] = []

    # =========================
    # PHASE: Practice (always 2-back)
    # =========================
    practice_trials = max(1, int(args.practice_trials))
    if not args.no_practice and practice_trials > 0:
        try:
            send_named('practice_start', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
        except Exception:
            pass
        while True:
            acc, _ = run_practice(win, 2, practice_trials)
            if acc >= PRACTICE_PASS_ACC:
                break
            # If failed, re-show very brief reminder before repeating
            show_practice_headsup(win)
        try:
            send_named('practice_end', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
        except Exception:
            pass

    # =========================
    # PHASE: Main Task (two sequential loads)
    # =========================
    total_blocks = 2 * blocks_per_load
    if trials_per_block <= 0:
        print("Note: trials_per_block is zero; main task is skipped.")
    block_counter = 0
    # Load switch occurs automatically after `blocks_per_load` blocks; `block_counter` continues across phases.
    for phase_idx, n_back in enumerate(load_order, start=1):
        # Phase-specific instructions / heads-up
        show_phase_instructions(win, n_back)
        # Also mark instructions_shown for each phase head-up, if desired
        try:
            send_named('instructions_shown', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
        except Exception:
            pass

        for within_phase_b in range(1, blocks_per_load + 1):
            block_counter += 1
            plans = generate_sequence(
                n_back,
                trials_per_block,
                target_rate=CFG_TARGET_RATE,
                lure_n_minus_1_rate=CFG_LURE_NM1,
                lure_n_plus_1_rate=CFG_LURE_NP1,
                max_consec_targets=CFG_MAX_CONSEC_TARGETS,
                fixed_iti_ms=CFG_FIXED_ITI_MS,
                include_lures=True,
            )
            block_accs: List[int] = []
            block_rts: List[float] = []

            # Run one block
            acc, mean_rt = run_block(
                win,
                block_idx=block_counter,
                n_back=n_back,
                plans=plans,
                is_practice=False,
                accs_out=block_accs,
                rts_out=block_rts,
                rows_out=all_rows,
            )

            # Persist rows periodically (per block)
            if all_rows:
                writer.writerows(all_rows)
                f.flush()
                overall_accs.extend(block_accs)
                overall_rts.extend([rt for rt in block_rts if rt is not None])
                all_rows.clear()

            # Break screen after each block except the final block of the session
            if block_counter < total_blocks:
                show_break(win, block_counter, acc, mean_rt)

    # Finish
    show_thanks(win)
    # Require explicit save/exit confirmation (ENTER) and avoid ESC here
    show_save_and_exit_prompt(win)

    # Final flush and close
    try:
        if all_rows:
            writer.writerows(all_rows)
        f.flush()
    finally:
        f.close()

    try:
        win.close()
    except Exception:
        pass

    # Mark experiment end
    try:
        send_named('experiment_end', parallel_port=GLOBAL_PARALLEL_PORT, eyelink=GLOBAL_EYELINK)
    except Exception:
        pass

    # Summary
    total_trials = (2 * blocks_per_load) * trials_per_block
    overall_acc = sum(overall_accs) / total_trials if total_trials else 0.0
    # Accuracy by target/non-target requires re-reading CSV rows; quick pass
    target_correct = 0
    target_total = 0
    nontarget_correct = 0
    nontarget_total = 0

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as rf:
            r = csv.DictReader(rf)
            for row in r:
                itarget = int(row["is_target"]) if row["is_target"] != "" else 0
                corr = int(row["correct"]) if row["correct"] != "" else 0
                if itarget == 1:
                    target_total += 1
                    if corr == 1:
                        target_correct += 1
                else:
                    nontarget_total += 1
                    if corr == 1:
                        nontarget_correct += 1
    except Exception:
        pass

    target_acc = (target_correct / target_total) if target_total else 0.0
    nontarget_acc = (nontarget_correct / nontarget_total) if nontarget_total else 0.0
    mean_rt = (sum(overall_rts) / len(overall_rts)) if overall_rts else None

    print("\n===== Session Summary =====")
    print(f"File: {CSV_PATH}")
    print(f"Trials: {total_trials}")
    print(f"Overall accuracy: {overall_acc*100:.1f}%")
    print(f"Target accuracy: {target_acc*100:.1f}% (n={target_total})")
    print(f"Non-target accuracy: {nontarget_acc*100:.1f}% (n={nontarget_total})")
    if mean_rt is not None:
        print(f"Mean RT (correct): {mean_rt:.0f} ms")
    print("===========================\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as e:
        raise e
    except Exception as e:
        # Ensure graceful close if window exists
        try:
            core.quit()
        except Exception:
            pass
        raise
