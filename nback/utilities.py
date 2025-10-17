"""Utility helpers for the N-back task (file/paths, time, text stimulus helpers)."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from psychopy import core, visual


def make_data_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in ("-", "_", ".")).strip()


def _default_wrap_width(win: visual.Window, margin: float = 0.95) -> float:
    try:
        aspect = win.size[0] / float(win.size[1])
    except Exception:
        aspect = 16/9
    return aspect * margin


def make_autosized_text(
    win: visual.Window,
    text: str,
    start_height: float = 0.07,
    min_height: float = 0.03,
    max_height_frac: float = 0.9,
    shrink_factor: float = 0.9,
    align: str = 'left',
    *,
    color = [1.0, 1.0, 1.0],
    font: str = "Arial",
) -> visual.TextStim:
    wrap_w = _default_wrap_width(win)
    h = start_height
    if align not in {'left','center'}:
        align = 'left'
    anchor_h = 'center'
    stim = visual.TextStim(
        win,
        text=text,
        color=color,
        font=font,
        height=h,
        wrapWidth=wrap_w,
        alignText=align,
        anchorHoriz=anchor_h,
        anchorVert='center',
    )
    try:
        while True:
            bb = getattr(stim, 'boundingBox', None)
            if not bb:
                stim.draw(); win.flip(); core.wait(0.01)
                bb = getattr(stim, 'boundingBox', None)
            if not bb:
                break
            bb_h = bb[1] if isinstance(bb, (list, tuple)) and len(bb) > 1 else 0
            if bb_h <= win.size[1] * max_height_frac:
                break
            h *= shrink_factor
            if h < min_height:
                break
            stim.height = h
    except Exception:
        pass
    return stim


__all__ = [
    "make_data_dir",
    "timestamp",
    "safe_filename",
    "_default_wrap_width",
    "make_autosized_text",
]
