# N-back Task (PsychoPy)

A comprehensive implementation of the N-back cognitive task built with PsychoPy for research in working memory and cognitive neuroscience.

## What is the N-back Task?

The N-back task is a well-established cognitive paradigm used to assess and train working memory. Participants are presented with a sequence of stimuli (letters in this implementation) and must identify when the current stimulus matches the one presented N trials ago. For example, in a 2-back task, participants press a key when the current letter matches the letter shown 2 trials earlier.

This implementation provides:

- **Two-load session design**: Each run includes two sequential N-back loads
  - Version A: 1-back → 3-back
  - Version B: 3-back → 1-back
- **Practice** always at 2-back with pass/fail feedback (optional)
- **Precise timing** with display refresh rate detection
- **Comprehensive data output** with trial-by-trial logging
- **Optional EEG/physiological markers** (LSL, Serial, Parallel port)
- **Cross-platform support** (Linux, macOS, Windows)

## Requirements

| Component | Version | Notes |
|-----------|---------|--------|
| **Operating System** | Linux, macOS, Windows | Tested on Ubuntu 20.04+, macOS 10.15+, Windows 10+ |
| **Python** | 3.10.x | Required by PsychoPy (3.11+ not yet supported) |
| **PsychoPy** | 2025.1.1 | Pinned for reproducibility |
| **Display** | Any | Fullscreen recommended for precise timing |

**Optional Dependencies** (pre-installed):

- `pylsl` >=1.16.2 - For Lab Streaming Layer markers
- `pyserial` >=3.5 - For serial port trigger devices

## Installation and Setup

### Option 1: Virtual Environment (Recommended)

This is the most reliable method for ensuring compatibility.

#### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/TH3PL4Y3R1/n_back.git
cd n_back

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install dependencies
.venv/bin/python -m pip install -U pip setuptools wheel
.venv/bin/python -m pip install -e .

# Verify installation
python check_psychopy.py
```

#### Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/TH3PL4Y3R1/n_back.git
cd n_back

# Create virtual environment (ensure Python 3.10.x is installed)
py -3.10 -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
.venv\Scripts\python -m pip install -U pip setuptools wheel
.venv\Scripts\python -m pip install -e .

# Verify installation
python check_psychopy.py
```

### Option 2: Conda Environment

Conda can help avoid compilation issues with GUI dependencies.

```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate n_back

# Verify installation
python check_psychopy.py
```

#### Conda Configuration (First Time Setup)

```bash
# Add conda-forge with strict priority (recommended)
conda config --prepend channels conda-forge
conda config --set channel_priority strict

# Update environment after changes to environment.yml or pyproject.toml
conda env update -f environment.yml --prune
```

### Verification

After installation, you should see output similar to:

```text
PsychoPy version: 2025.1.1
```

**Note**: The `environment.yml` preinstalls `wxpython` from conda-forge to avoid slow/fragile source builds.

#### Environment Strategy (Why pip for PsychoPy 2025.1.1?)

PsychoPy 2025.1.1 (the version this project pins) is not yet available on conda-forge at the time of writing. Installing `psychopy` from conda would give you an older release. To ensure the desired version while avoiding a lengthy `wxPython` source build, the workflow is:

1. Let conda install binary `wxpython` (and other compiled GUI dependencies) from conda-forge.
2. Use pip (inside the environment) to install the exact `psychopy==2025.1.1` plus pure-Python/ wheel dependencies.

This is handled automatically by `environment.yml`: after solving the binary dependencies with conda it runs `pip install -e .`, which installs PsychoPy and the marker libraries from `pyproject.toml`. Keep that pip step in place instead of adding `psychopy` to the conda dependencies list; otherwise conda will downgrade the version.

Quick verification after creation:

```bash
conda activate n_back
python - <<'PY'
import psychopy, wx
print('PsychoPy version:', psychopy.__version__)
print('wxPython version:', wx.version())
PY
```

Expected: PsychoPy 2025.1.1 and wxPython 4.2.x.

If PsychoPy shows an earlier version, you likely installed the conda package; recreate the env or run `python -m pip install --upgrade --force-reinstall psychopy==2025.1.1`.

## Quick Start

### Basic Usage

Run a complete two-load experiment with default settings (Version A: 1→3, 3 blocks per load, 60 trials per block):

```bash
python nback_task.py --participant test
```

Run Version B (3→1) in windowed mode, no practice, 1 block per load with 10 trials:

```bash
python nback_task.py --participant pilot --version B --no-practice --blocks-per-load 1 --trials 10 --windowed
```

### Usage Examples

**Development/Testing**:

```bash
python nback_task.py --participant dev --windowed                # Windowed mode for debugging
python nback_task.py --participant test --no-practice            # Skip practice phase
python nback_task.py --participant test --practice-trials 10     # Custom practice length
```

**Research Configurations**:

```bash
python nback_task.py --participant P001 --version A --blocks-per-load 4 --trials 100   # 1→3 with 4 blocks per load
python nback_task.py --participant P001 --version B --seed 1234                        # 3→1 with fixed RNG seed
python nback_task.py --participant P001 --soa-ms 1800 --target-rate 0.4               # Custom timing and target rate
```

## Command-Line Interface

### Required Arguments

- `--participant, -p` (str): Participant ID for output filename

### Core Task Parameters

- `--version` (str): Load order. `A` for 1→3, `B` for 3→1. Default: `A`
- `--blocks-per-load` (int): Number of blocks per load. Default: `3`
- `--trials` (int): Trials per block. Default: `60`

### Practice Phase

- `--no-practice` (flag): Skip practice phase
- `--practice-trials` (int): Number of practice trials. Default: `20`

### Display and Timing

- `--windowed` (flag): Run windowed (for debugging only; reduces timing precision)
- `--list-screens` (flag): Enumerate detected physical displays (with indices) and exit
- `--screen` (int): Force use of a specific screen index (e.g., 0 for primary high-refresh monitor)
- `--soa-ms` (int): Constant stimulus onset asynchrony in milliseconds. Default: `2000`. Controls total trial duration and replaces ITI jitter.
- `--kb-backend` (str): Keyboard backend `{event, ptb}`. Default: `event`. Use `ptb` for lower-latency input if supported on your OS.

### Advanced Configuration

- `--target-rate` (float): Target rate (0-1). Default: `0.30`
- `--lure-nminus1` (float): Rate of n-1 lures. Default: `0.05`
- `--lure-nplus1` (float): Rate of n+1 lures. Default: `0.05`
- `--max-consec-targets` (int): Max consecutive targets. Default: `1`
- `--seed` (int): Random seed for reproducibility

## Task Flow

1. **Informed Consent**: Displays consent form from `texts/informed_consent.txt`
2. **Instructions**: Session overview including the two-load order (e.g., 1→3)
3. **Practice Phase** (optional): Always 2-back with feedback and repeat until criterion
4. **Main Task**: Two phases back-to-back with breaks between blocks — Phase 1: 3 blocks at the first load (e.g., 1-back); Phase 2: 3 blocks at the second load (e.g., 3-back). The load switches automatically after block 3.

5. **Data Export**: Automatic CSV and metadata JSON export

### Participant Instructions

- **Target Response**: Press SPACEBAR when current letter matches the one N trials ago
- **Non-target**: Do nothing for all other letters
- **Breaks**: Rest between blocks; press ENTER to continue
- **Exit**: Press ESC to quit (data saved only if task completes normally)

## Data Output

### File Structure

```text
data/
|- nback_{participant}_{YYYYMMDD_HHMMSS}.csv     # Trial data
\- nback_{participant}_{YYYYMMDD_HHMMSS}.meta.json  # Metadata
```

### Trial Data Columns

| Column | Type | Description |
|--------|------|-------------|
| `participant_id` | string | Participant identifier |
| `session_timestamp` | string | Session start time (YYYYMMDD_HHMMSS) |
| `block_idx` | int | Block number (1-indexed) |
| `trial_idx` | int | Trial number within block (1-indexed) |
| `n_back` | int | N-back level for this trial |
| `stimulus` | string | Letter presented |
| `is_target` | int | 1=target, 0=non-target |
| `lure_type` | string | "none", "n-1", or "n+1" |
| `iti_ms` | int | Inter-trial interval (milliseconds) |
| `stim_onset_time` | float | Stimulus onset timestamp (seconds) |
| `response_key` | string | Key pressed ("space" or empty) |
| `rt_ms` | float | Reaction time (milliseconds, empty if no response) |
| `correct` | int | 1=correct, 0=incorrect |
| `marker_code_stim` | int | Stimulus onset marker code |
| `marker_code_resp` | int | Response marker code (empty if no response) |

See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for complete field specifications.

### Metadata JSON Contents

Each session also writes a sidecar `*.meta.json` capturing reproducibility/context parameters. Key fields:

- `participant_id`, `session_timestamp`
- Task config: `practice_n_back` (always 2), `load_order` (e.g., [1,3]), `blocks_per_load`, `total_blocks`, `trials_per_block`, practice & lure/target rates, seed
- `letters`: Stimulus alphabet after exclusions
- `psychopy_version`
- Display context: `display_refresh_hz` (measured), `window_fullscreen` (bool), `screen_index` (if specified)
- Timing model: `soa_ms` (constant SOA), `fixed_iti_ms` (derived from SOA and response window)
- Input backend: `kb_backend` ("event" or "ptb")
- Any CLI-overridden parameters (e.g., target rate, lure rates)

Use this file when auditing timing discrepancies or reproducing sequences (combine with the seed).

## Physiological Markers (Optional)

The task includes marker support for EEG/physiological recordings but is disabled by default.

### Enable Markers

1. Edit `nback/markers.py`
2. Set `ENABLE_MARKERS = True`
3. Uncomment and configure ONE marker method:

**Lab Streaming Layer (LSL)**:

```python
# Uncomment LSL section in markers.py
# Ensure pylsl receiver is running
```

**Serial Port**:

```python
# Uncomment Serial section in markers.py
# Update port name: '/dev/ttyUSB0' (Linux) or 'COM3' (Windows)
```

**Parallel Port**:

```python
# Uncomment Parallel section in markers.py  
# Update address: typically 0x0378
```

### Marker Codes

| Event | Code |
|-------|------|
| Consent shown | 10 |
| Block start | 20 |
| Fixation onset | 30 |
| Target stimulus | 41 |
| Non-target stimulus | 42 |
| N-1 lure | 43 |
| N+1 lure | 44 |
| Response registered | 50 |
| Block end | 70 |
| Task complete | 90 |

## Repository Structure

```text
n_back/
|- README.md                  # This file
|- DATA_DICTIONARY.md         # Complete data field descriptions
|- environment.yml            # Conda environment specification
|- pyproject.toml             # Project metadata and dependencies
|- check_psychopy.py          # Installation verification script
|- nback_task.py              # Main task script (two-load design)
|- nback/                     # Task modules
|  |- __init__.py
|  |- markers.py              # Marker/trigger integration
|  \- sequences.py            # Sequence generation logic
|- scripts/                   # Utility scripts
|  |- timing_diagnostics.py   # Display timing assessment
|  |- preview_seq.py          # Sequence preview tool
|  \- local_sequence_check.py # Sequence validation
\- texts/                     # Instruction text files
  |- informed_consent.txt
  |- instructions_welcome.txt
  \- ... (other instruction files)
```

## Timing and Performance

### Timing Precision

- **Fullscreen mode** (default): Optimal timing precision using hardware vsync
- **Windowed mode** (`--windowed`): Reduced precision, for debugging only
- **Display refresh detection**: Automatic at startup, logged in metadata
- **Multi-monitor selection**: Use `--list-screens` to enumerate physical displays, then `--screen N` to force window on a specific monitor (e.g., primary high-refresh panel)
- **Frame-synced presentation**: All stimuli locked to display refresh
- **Hardware keyboard**: Low-latency input when available

### Constant SOA (Stimulus Onset Asynchrony)

- The task uses a constant SOA for predictable trial timing. The current default is `--soa-ms 2500` (2.5 seconds per trial).
- Within each trial:
  - Stimulus duration: 500 ms
  - Response window: equals SOA (responses accepted until next onset)
  - Fixation fills the remainder after the stimulus until the next onset
- Legacy ITI jitter has been removed. Adjust `--soa-ms` to change overall pacing.

### Keyboard backend selection

- Choose the keyboard input backend via `--kb-backend {event,ptb}`. Default: `event` (safe, compatible).
- `ptb` uses the Psychtoolbox hardware keyboard for lower-latency input. On some Linux systems, this may require real-time scheduling privileges; if unavailable, the task falls back to the `event` backend. If you encounter startup issues with `ptb`, use `--kb-backend event`.

### Performance Monitoring

Run timing diagnostics to assess your system:

```bash
python scripts/timing_diagnostics.py --fullscr
```

### Sequence Preview

Preview generated sequences without running the full task:

```bash
# Preview 2-back sequence with 20 trials
PYTHONPATH=. python scripts/preview_seq.py 2 20

# With specific seed
PYTHONPATH=. python scripts/preview_seq.py 2 20 1234
```

## Scripts

Utility scripts to support setup and validation:

- `scripts/timing_diagnostics.py`: Assess display timing and refresh stability
- `scripts/preview_seq.py`: Print a generated sequence for given N/trials (optional seed)
- `scripts/local_sequence_check.py`: Validate generated sequences against core constraints

### Smoke Test

Validate the two-load design with tiny sessions (windowed, no practice):

```bash
python scripts/smoke_test.py
```

This runs Version A and B with 1 block per load and verifies that both loads appear in the saved logs and that the switch occurs after the first block.

Run with `PYTHONPATH=.` when calling from the repo root so they can import the `nback` package.

## Troubleshooting

### Installation Issues

**wxPython build errors** (Linux):

- Use conda installation: `conda env create -f environment.yml`
- Ensure conda-forge channel is configured with strict priority

**Python version conflicts**:

- Ensure Python 3.10.x is installed and specified correctly
- On Windows: `py -3.10 -m venv .venv`
- Check version: `python --version`

**PsychoPy import failures**:

- Verify installation: `python check_psychopy.py`
- Check virtual environment activation
- Reinstall if needed: `pip install --force-reinstall psychopy==2025.1.1`

### Runtime Issues

**Display/timing problems**:

- Always use fullscreen mode for experiments (`--windowed` is debugging only)
- Run timing diagnostics: `python scripts/timing_diagnostics.py --fullscr`
- Close other applications that might affect display performance
- If the wrong refresh rate is detected (e.g. using a secondary 60/100 Hz monitor instead of a 144/165 Hz primary), list screens:

  ```bash
  python nback_task.py --list-screens
  ```

  Then select the desired one:

  ```bash
  python nback_task.py --screen 0   # replace 0 with the index you want
  ```

- If PsychoPy reports an unexpected older version, recreate the env (ensure pip installed `psychopy==2025.1.1`).
- VS Code "No module named psychopy" issue: make sure the selected interpreter is the `n_back` conda env (or activated venv) before running.

**Keyboard backend issues (Linux/PTB)**:

- If the PTB keyboard backend crashes or hangs at start, it's likely due to missing real-time privileges. Run with `--kb-backend event` to use the safe fallback, or consult PsychoPy/Psychtoolbox docs to enable the PTB backend on your system.

**Task not starting**:

- Check file permissions on `texts/` directory
- Ensure `data/` directory exists (created automatically)
- Verify all instruction text files are present

**Data not saving**:

- Check write permissions in `data/` directory
- Avoid special characters in participant IDs
- Complete task normally (don't force-quit)

## Customization

### Instruction Text

Edit files in `texts/` directory to customize instructions:

- `informed_consent.txt` - Consent form
- `instructions_welcome.txt` - Welcome message
- `instructions_practice_headsup.txt` - Practice instructions
- `instructions_task_headsup.txt` - Main task instructions
- Other instruction files for breaks, feedback, etc.

### Task Parameters

Key parameters can be modified via command line or by editing defaults in `nback_task.py`:

- Stimulus letters (default: A-Z excluding I, O, Q)
- Timing parameters (ITI range, stimulus duration)
- Sequence constraints (target rate, lure rates)
- Display settings (colors, fonts, sizes)

## Contributing

We welcome contributions to improve the N-back task implementation. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Code style and standards
- Testing procedures
- Pull request process
- Bug reporting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this implementation in your research, please cite:

```bibtex
@misc{nback_psychopy,
  title={N-back Task Implementation in PsychoPy},
  author={[Add author information]},
  year={2025},
  url={https://github.com/TH3PL4Y3R1/n_back}
}
```

## Support

- **Documentation**: See `DATA_DICTIONARY.md` for complete field descriptions
- **Issues**: Report bugs or request features via GitHub Issues
- **Questions**: For usage questions, please check existing issues first

---

**Version**: 1.1.0  
**Last Updated**: October 2025  
**Maintainer**: [Add maintainer contact information]
