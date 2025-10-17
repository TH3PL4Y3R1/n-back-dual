from __future__ import annotations

"""Marker transport helpers for the PsychoPy N-back task.

This module centralizes event marker codes and provides simple hooks to emit
them over different backends (LSL, serial, or parallel). By default, markers
are disabled to keep the task self-contained; enable them only when the
corresponding hardware/software is available and configured.
"""

from typing import Optional

from psychopy import core

# Toggle markers here
ENABLE_MARKERS = False

# Marker codes
MARK_CONSENT_SHOWN = 10
MARK_BLOCK_START = 20
MARK_FIXATION_ONSET = 30
MARK_STIM_TARGET = 41
MARK_STIM_NONTARGET = 42
MARK_STIM_LURE_N_MINUS_1 = 43
MARK_STIM_LURE_N_PLUS_1 = 44
MARK_RESPONSE_REGISTERED = 50
MARK_BLOCK_END = 70
MARK_THANK_YOU = 90

# -- Optional integration stubs (commented) --
# _lsl_outlet = None
# def _get_lsl_outlet():
#     global _lsl_outlet
#     if _lsl_outlet is None:
#         from pylsl import StreamInfo, StreamOutlet
#         info = StreamInfo(name='Markers', type='Markers', channel_count=1,
#                           nominal_srate=0, channel_format='int32', source_id='nback-markers')
#         _lsl_outlet = StreamOutlet(info)
#     return _lsl_outlet

# _serial_port = None
# def _get_serial_port():
#     global _serial_port
#     if _serial_port is None:
#         import serial
#         _serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=0)
#     return _serial_port

# _parallel_port = None
# def _get_parallel_port():
#     global _parallel_port
#     if _parallel_port is None:
#         from psychopy import parallel
#         _parallel_port = parallel.ParallelPort(address=0x0378)
#     return _parallel_port


def send_marker(code: int, info: Optional[dict] = None) -> None:
    """Send a marker code via the configured backend if enabled.

    Parameters
    - code: Numeric event code (see constants above)
    - info: Optional extra context for future backends; currently unused
    """
    if not ENABLE_MARKERS:
        return
    # --- LSL send ---
    # outlet = _get_lsl_outlet()
    # outlet.push_sample([int(code)])

    # --- Serial send ---
    # ser = _get_serial_port()
    # ser.write(bytes([int(code) & 0xFF]))

    # --- Parallel port send ---
    # p = _get_parallel_port()
    # p.setData(int(code) & 0xFF)
    # core.wait(0.005)
    # p.setData(0)
