from __future__ import annotations

"""Marker transport helpers for the PsychoPy N-back task.

This module centralizes event marker codes and provides simple hooks to emit
them over the same backends used by the Bosch task (parallel port and EyeLink).
By default, markers are disabled to keep the task self-contained; enable them
only when hardware/software is available and configured.
"""

from typing import Optional, Dict, Any

# Toggle markers here (keep False by default; set to True when hardware is available)
ENABLE_MARKERS = False

# Default numeric codes for named triggers. These can be changed by client code if needed.
# Chosen to be unique and <=255 so they fit on an 8-bit parallel port output.
TRIGGERS: Dict[str, int] = {
    'experiment_start': 1,
    'consent_shown': 2,
    'instructions_shown': 3,
    'practice_start': 10,
    'practice_end': 11,
    'block_ll_start': 20,  # low load block start
    'block_ll_end': 21,
    'block_hl_start': 30,  # high load block start
    'block_hl_end': 31,
    'stim_presentation': 40,
    'fixation_onset': 41,
    'response_ll': 50,
    'response_hl': 51,
    'debrief_shown': 90,
    'experiment_end': 99,
}


def send_marker(code: int,
                parallel_port: Optional[Any] = None,
                eyelink: Optional[Any] = None) -> None:
    """Send a numeric marker via Bosch-compatible backends.

    Parameters
    - code: numeric marker value (masked to 0-255 for parallel port)
    - parallel_port: psychopy.parallel.ParallelPort instance (optional)
    - eyelink: pylink.EyeLink instance (optional)

    Behavior (mirrors bosch-task):
    - If ENABLE_MARKERS is False, this is a no-op.
    - If `parallel_port` is provided, call setData(code) without auto-clearing.
    - If `eyelink` is provided, call sendMessage(str(code)).
    """
    if not ENABLE_MARKERS:
        return

    # Parallel port send
    if parallel_port is not None:
        try:
            parallel_port.setData(int(code) & 0xFF)
        except Exception:
            # don't crash the experiment if marker backend fails
            pass

    # EyeLink send (expects a string)
    if eyelink is not None:
        try:
            eyelink.sendMessage(str(code))
        except Exception:
            pass


def send_named(name: str,
               parallel_port: Optional[Any] = None,
               eyelink: Optional[Any] = None,
               info: Optional[Dict[str, Any]] = None) -> None:
    """Lookup a named trigger and send it via the available backends.

    Parameters
    - name: one of the keys in TRIGGERS (raises KeyError if unknown)
    - other args passed to send_marker
    """
    code = TRIGGERS[name]
    send_marker(code, parallel_port=parallel_port, eyelink=eyelink)


def set_enable(value: bool) -> None:
    """Enable or disable marker sending at runtime."""
    global ENABLE_MARKERS
    ENABLE_MARKERS = bool(value)


def set_trigger_code(name: str, code: int) -> None:
    """Change the numeric code associated with a named trigger."""
    if name not in TRIGGERS:
        raise KeyError(f'Unknown trigger name: {name}')
    TRIGGERS[name] = int(code) & 0xFF


def create_parallel_port(address: int = 0x03BC):
    """Create and return a PsychoPy ParallelPort instance.

    This helper avoids importing psychopy.parallel at module import time and
    uses the Bosch-task default address (0x03BC) so the `full-task` code can
    quickly plug into the same hardware wiring used by `bosch-task`.

    Usage:
        from psychopy import parallel
        pp = create_parallel_port()  # default addr 0x03BC

    Returns the ParallelPort instance or raises the underlying import error.
    """
    from psychopy import parallel
    # set the port address for module-level operations that might use parallel.setPortAddress
    try:
        parallel.setPortAddress(address)
    except Exception:
        # some psychopy versions expose setPortAddress differently; ignore if not present
        pass
    return parallel.ParallelPort(address=address)

