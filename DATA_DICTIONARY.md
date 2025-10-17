# N-back Task — Data Dictionary

## Overview

This document defines every field produced by the N-back PsychoPy task. It ensures anyone can interpret the dataset without reading the source code.

For additional information, see:

- [README.md](README.md) - General usage and setup

## File naming and location

- **Folder**: `./data/`
- **Filename template**: `nback_{participantID}_{YYYYMMDD_HHMMSS}.csv`
- **Metadata sidecar**: `nback_{participantID}_{YYYYMMDD_HHMMSS}.meta.json`
- **One file per session**: If multiple sessions occur in the same second, the timestamp is identical; the participant or later start time will differ. Keeping sessions separate is recommended.

## Task parameters captured in each run (metadata sidecar .meta.json)

The following parameters are saved in the JSON metadata file accompanying each CSV data file:

| Parameter               | Type             | Description                                                            |
|-------------------------|------------------|------------------------------------------------------------------------|
| `participant_id`        | string           | Participant identifier                                                 |
| `session_timestamp`     | string           | Session start time (`YYYYMMDD_HHMMSS`)                                 |
| `practice_n_back`       | int              | Practice N level (fixed at 2)                                          |
| `load_order`            | list of ints     | Two-load order for the session (e.g., `[1, 3]` or `[3, 1]`)           |
| `blocks_per_load`       | int              | Number of blocks in each load                                          |
| `total_blocks`          | int              | Total blocks across both loads                                         |
| `trials_per_block`      | int              | Trials per block                                                       |
| `practice_trials`       | int              | Number of practice trials                                              |
| `practice_target_rate`  | float            | Target rate in practice (0–1)                                          |
| `practice_has_lures`    | bool             | Whether practice includes lures                                        |
| `target_rate`           | float            | Target rate in main task (0–1)                                         |
| `lure_nminus1_rate`     | float            | Rate of n-1 lures (0–1)                                                |
| `lure_nplus1_rate`      | float            | Rate of n+1 lures (0–1)                                                |
| `max_consec_targets`    | int              | Maximum consecutive targets allowed                                    |
| `seed`                  | int or null      | Random seed (null if not specified)                                    |
| `letters`               | list of strings  | Available stimulus letters                                             |
| `psychopy_version`      | string or null   | PsychoPy version used                                                  |
| `display_refresh_hz`    | float or null    | Detected display refresh rate at startup                               |
| `window_fullscreen`     | bool             | Whether task ran in fullscreen (recommended for timing)                |
| `screen_index`          | int or null      | Display index when multiple monitors are present (0 = primary)         |
| `soa_ms`                | int              | Constant stimulus onset asynchrony in milliseconds (default 2500)      |
| `fixed_iti_ms`          | int              | Derived ITI used, computed as `soa_ms - stim_dur_ms` (default 2000)    |
| `kb_backend`            | string           | Keyboard backend: `event` (default) or `ptb`                           |

## Trial-level columns

| Column name         | Description                                   | Type    | Values                               |
|---------------------|-----------------------------------------------|---------|--------------------------------------|
| `participant_id`    | Participant code                              | string  | alphanumeric                         |
| `session_timestamp` | Session start time (file timestamp)           | string  | `YYYYMMDD_HHMMSS`                    |
| `block_idx`         | Block index (1-based)                         | int     | `1..blocks`                          |
| `trial_idx`         | Trial index within block (1-based)            | int     | `1..trials_per_block`                |
| `n_back`            | N level for block                             | int     | `1`, `2`, or `3`                     |
| `stimulus`          | Letter shown                                  | string  | `A-Z` excluding I/O/Q by default     |
| `is_target`         | Target trial flag                             | int     | `1` = target, `0` = non-target       |
| `lure_type`         | Lure category                                 | string  | `"none"`, `"n-1"`, `"n+1"`           |
| `iti_ms`            | Planned inter-trial interval                  | int     | milliseconds                         |
| `stim_onset_time`   | Stimulus onset (returned by window.flip)      | float   | seconds (high-resolution timestamp)  |
| `response_key`      | Key pressed                                   | string  | key name (e.g., `"space"`) or empty  |
| `rt_ms`             | Reaction time from stimulus onset             | float   | milliseconds; empty if no response   |
| `correct`           | Response accuracy                             | int     | `1` = correct, `0` = incorrect       |
| `marker_code_stim`  | Marker code at stimulus onset                 | int     | see marker coding                    |
| `marker_code_resp`  | Marker code at response                       | int     | see marker coding or empty           |

## Marker coding

Marker codes are sent at specific events (if enabled in `nback/markers.py`). Default: transport code is a no-op; call sites exist.

| Event | Code | Description |
|-------|------|-------------|
| consent_shown | 10 | Informed consent screen displayed |
| block_start | 20 | New block started |
| fixation_onset | 30 | Fixation cross presented |
| stimulus_target | 41 | Target stimulus presented |
| stimulus_nontarget | 42 | Non-target stimulus presented |
| stimulus_lure_n_minus_1 | 43 | N-1 lure stimulus presented |
| stimulus_lure_n_plus_1 | 44 | N+1 lure stimulus presented |
| response_registered | 50 | Participant response detected |
| block_end | 70 | Block completed |
| thank_you | 90 | Task completion screen |

## Sequence constraints

1. No targets in first N trials
2. Target rate ≈ target_rate ±1 trial
3. Max consecutive targets = 1 (unless allowed)
4. Optional lures; never double-count as targets
5. Avoid unintended repeats for N>1
6. Max identical-letter run = 2 (unless required)
7. Soft balance letter frequency
8. Retry until constraints satisfied or max_attempts reached

## Missing values policy

When no response is recorded:

- `response_key = ""` (empty string)
- `rt_ms = ""` (empty string)
- `correct = 0`
- `marker_code_resp = ""` (empty string)

## Example row

```csv
participant_id,session_timestamp,block_idx,trial_idx,n_back,stimulus,is_target,lure_type,iti_ms,stim_onset_time,response_key,rt_ms,correct,marker_code_stim,marker_code_resp
P001,20250811_113207,1,37,2,K,1,none,712,45.382,space,421.7,1,41,50
```

## Versioning

- **Version**: 1.1.0
- **Last updated**: 2025-08-20
- **Maintainer**: N-back Task Contributors

**Changelog**:

- **1.1.0** — Add metadata fields `screen_index`, `soa_ms`, `fixed_iti_ms`, and `kb_backend`; clarify constant SOA timing model (default SOA 2500 ms).
- **1.0.3** — Enhanced formatting, added cross-references, improved table structure
- **1.0.2** — Document `display_refresh_hz` and `window_fullscreen` in metadata; minor clarifications
- **1.0.1** — Align docs with code: marker codes 41/42/43/44 and response 50; timestamp format `YYYYMMDD_HHMMSS`; empty string policy for missing
- **1.0.0** — Initial dictionary covering trial CSV, marker scheme, and validation rules
