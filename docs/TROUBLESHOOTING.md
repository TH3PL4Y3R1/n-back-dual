# Troubleshooting Guide

This guide helps resolve common issues encountered when setting up and running the N-back task.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Problems](#runtime-problems)
- [Display and Timing Issues](#display-and-timing-issues)
- [Data Output Problems](#data-output-problems)
- [Platform-Specific Issues](#platform-specific-issues)
- [Performance Optimization](#performance-optimization)
- [Getting Help](#getting-help)

## Installation Issues

### Python Version Problems

**Issue**: `ModuleNotFoundError: No module named 'psychopy'` or version conflicts

**Cause**: PsychoPy requires Python 3.10.x specifically

**Solutions**:

1. **Check Python version**:
   ```bash
   python --version
   # Should show 3.10.x
   ```

2. **Install correct Python version**:
   - **Ubuntu/Debian**: `sudo apt install python3.10 python3.10-venv`
   - **macOS**: Use Homebrew: `brew install python@3.10`
   - **Windows**: Download from python.org, ensure you install 3.10.x

3. **Create virtual environment with correct Python**:
   ```bash
   # Linux/macOS
   python3.10 -m venv .venv
   
   # Windows
   py -3.10 -m venv .venv
   ```

### wxPython Build Errors (Linux)

**Issue**: Long compilation times or build failures for wxPython

**Error messages**:
```
Building wheel for wxpython (pyproject.toml) ... error
ERROR: Failed building wheel for wxpython
```

**Solution**: Use conda environment instead of pip:

```bash
# Use conda to avoid building from source
conda env create -f environment.yml
conda activate n_back
```

**Alternative**: Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get install python3.10-dev libgtk-3-dev libwebkitgtk-3.0-dev
```

### PsychoPy Import Failures

**Issue**: `ImportError` when importing PsychoPy components

**Common causes and solutions**:

1. **Missing system libraries** (Linux):
   ```bash
   # Install required packages
   sudo apt-get install python3-dev python3-numpy python3-scipy
   sudo apt-get install libusb-1.0-0-dev portaudio19-dev libasound2-dev
   ```

2. **Virtual environment not activated**:
   ```bash
   # Ensure virtual environment is active
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Corrupted installation**:
   ```bash
   # Reinstall PsychoPy
   pip uninstall psychopy
   pip install psychopy==2025.1.1
   ```

### Permission Errors

**Issue**: Permission denied when creating virtual environment or installing packages

**Solutions**:

1. **Don't use sudo with pip** (corrupts environments)
2. **Create venv in user directory**:
   ```bash
   python3 -m venv ~/n_back_env
   ```
3. **Check directory permissions**:
   ```bash
   ls -la .venv/
   ```

## Runtime Problems

### Task Won't Start

**Issue**: Script runs but no window appears or immediate crash

**Diagnostic steps**:

1. **Test PsychoPy installation**:
   ```bash
   python check_psychopy.py
   ```

2. **Run in windowed mode for debugging**:
   ```bash
   python nback_task.py --participant test --windowed
   ```

3. **Check for missing files**:
   ```bash
   ls texts/  # Should contain instruction files
   ```

4. **Verify data directory**:
   ```bash
   mkdir -p data  # Create if missing
   ```

### Immediate Crashes

**Issue**: Task crashes during startup

**Common causes**:

1. **Display driver issues**:
   - Update graphics drivers
   - Try windowed mode: `--windowed`
   - Disable hardware acceleration if needed

2. **Audio system conflicts**:
   ```python
   # In nback_task.py, add at startup:
   from psychopy import prefs
   prefs.hardware['audioLib'] = ['pygame']
   ```

3. **File encoding issues**:
   - Ensure text files in `texts/` use UTF-8 encoding
   - Check for special characters in instruction files

### Keyboard Input Not Working

**Issue**: Task doesn't respond to keypresses

**Solutions**:

1. **Window focus**: Click on task window to ensure focus
2. **Keyboard layout**: Ensure US keyboard layout for key names
3. **Hardware keyboard fallback**: Task should gracefully degrade
4. **Alternative keys**: Try different keys if space/enter don't work

### Task Freezes or Hangs

**Issue**: Task becomes unresponsive

**Immediate actions**:
1. **Emergency exit**: Press Ctrl+C in terminal
2. **Force quit**: Alt+F4 (Windows) or Cmd+Q (macOS)

**Prevention**:
1. **Close other applications** that might interfere
2. **Use fullscreen mode** for better resource allocation
3. **Check system resources** (RAM, CPU usage)

## Display and Timing Issues

### Poor Timing Performance

**Issue**: Dropped frames or inconsistent timing

**Diagnosis**:
```bash
# Run timing diagnostics
python scripts/timing_diagnostics.py --fullscr
```

**Solutions**:

1. **Use fullscreen mode** (never windowed for experiments):
   ```bash
   python nback_task.py --participant test  # Default is fullscreen
   ```

2. **Close other applications**:
   - Web browsers
   - Video players
   - Screen savers
   - System monitoring tools

3. **Disable visual effects** (Windows):
   - Turn off Windows animations
   - Disable desktop composition

4. **Graphics settings**:
   - Update graphics drivers
   - Disable VSync if causing issues
   - Check refresh rate matches monitor

### Screen Resolution Problems

**Issue**: Task window too large/small or positioned incorrectly

**Solutions**:

1. **Check display settings**:
   ```python
   # In scripts/timing_diagnostics.py, check detected resolution
   ```

2. **Multiple monitors**: Ensure task runs on primary display

3. **High DPI displays**: May need scaling adjustments

### Refresh Rate Detection Issues

**Issue**: Incorrect or failed refresh rate detection

**Check detection**:
```bash
# Look for this line in task output:
# "Detected display refresh: XX.X Hz"
```

**Solutions**:

1. **Use standard refresh rates**: 60Hz, 120Hz, 144Hz
2. **Check monitor specifications**
3. **Update display drivers**
4. **Try different display ports/cables**

## Data Output Problems

### Files Not Created

**Issue**: No CSV or JSON files in data/ directory

**Diagnostic checks**:

1. **Directory exists and writable**:
   ```bash
   ls -la data/
   mkdir -p data  # Create if missing
   ```

2. **Disk space available**:
   ```bash
   df -h .  # Check free space
   ```

3. **Complete task normally**: Data saved only on normal completion

### Incomplete Data Files

**Issue**: CSV file missing trials or truncated

**Causes**:
- Task terminated early (ESC pressed)
- System crash during experiment
- Write permission issues

**Solutions**:
- Complete task normally (press Enter at final screen)
- Check logs for error messages
- Ensure stable system during experiments

### Character Encoding Issues

**Issue**: Strange characters in output files

**Solutions**:
- Ensure UTF-8 encoding in text editors
- Check instruction text files encoding
- Verify participant ID contains only ASCII characters

## Platform-Specific Issues

### Windows Issues

**Common problems**:

1. **PowerShell execution policy**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Path issues with Python**:
   - Use `py -3.10` instead of `python3`
   - Ensure Python added to PATH during installation

3. **Antivirus interference**:
   - Add project directory to antivirus exclusions
   - Temporarily disable real-time scanning for testing

### macOS Issues

**Common problems**:

1. **macOS security prompts**:
   - Allow terminal access to screen recording
   - Grant accessibility permissions if requested

2. **Homebrew Python conflicts**:
   ```bash
   # Use system Python 3.10 if available
   /usr/bin/python3 --version
   ```

3. **M1/M2 Mac compatibility**:
   - Ensure PsychoPy version supports Apple Silicon
   - Use Rosetta if needed: `arch -x86_64 python ...`

### Linux Issues

**Common problems**:

1. **Audio system conflicts** (PulseAudio/ALSA):
   ```bash
   # Install audio development packages
   sudo apt-get install libasound2-dev portaudio19-dev
   ```

2. **Graphics driver issues**:
   - Prefer open-source drivers for stability
   - Check OpenGL support: `glxinfo | grep OpenGL`

3. **Wayland vs X11**:
   - Some timing issues with Wayland
   - Try X11 session if available

## Performance Optimization

### System Configuration

**For optimal timing performance**:

1. **Disable power management**:
   - Set to "High Performance" mode
   - Disable CPU throttling
   - Turn off screen savers

2. **Close unnecessary processes**:
   ```bash
   # Check CPU usage
   top    # Linux/macOS
   taskmgr  # Windows
   ```

3. **Network stability**:
   - Disable WiFi power saving
   - Use wired connection if needed for markers

### PsychoPy Optimization

**Configuration tweaks**:

1. **Hardware preferences**:
   ```python
   from psychopy import prefs
   prefs.hardware['audioLib'] = ['pygame']  # Lighter audio
   ```

2. **Logging levels**:
   ```python
   import logging
   logging.getLogger('psychopy').setLevel(logging.WARNING)
   ```

### Memory Management

**For long experiments**:

1. **Monitor memory usage** during development
2. **Clear variables** between blocks if needed
3. **Restart between sessions** for multi-session studies

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** thoroughly
2. **Search existing issues** on GitHub
3. **Test with minimal example**:
   ```bash
   python nback_task.py --participant test --windowed --version A --blocks-per-load 1 --trials 5 --no-practice
   ```

### Information to Include

When reporting issues, include:

**System Information**:
```bash
# Python version
python --version

# Operating system
uname -a  # Linux/macOS
systeminfo  # Windows

# PsychoPy version
python -c "import psychopy; print(psychopy.__version__)"

# Hardware info
python scripts/timing_diagnostics.py
```

**Error Details**:
- Complete error message/traceback
- Exact command that failed
- Steps to reproduce
- Expected vs actual behavior

### Common Log Locations

- **Console output**: Full terminal output
- **PsychoPy logs**: Usually in user home directory
- **System logs**: Check system event logs for crashes

### Emergency Recovery

**If task is stuck**:
1. **Ctrl+C**: Interrupt in terminal
2. **ESC key**: Built-in quit mechanism
3. **Alt+F4/Cmd+Q**: Force application quit
4. **System restart**: Last resort

**Data recovery**:
- Check for partial CSV files in data/
- Look for temporary files
- Check system temp directories

### Getting Support

1. **Documentation**: README.md, API.md, this guide
2. **GitHub Issues**: Report bugs or ask questions
3. **Code review**: Check source code for implementation details
4. **Community**: Research community forums and PsychoPy user groups

---

If this guide doesn't solve your problem, please open a GitHub issue with detailed information about your system and the specific error you're encountering.