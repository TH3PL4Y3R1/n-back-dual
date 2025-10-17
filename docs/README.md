# N-back Task Documentation

Welcome to the comprehensive documentation for the N-back Task implementation in PsychoPy. This documentation covers everything from basic setup to advanced customization and troubleshooting.

## Quick Start

New to the N-back task? Start here:

1. **[README.md](../README.md)** - Main project overview, installation, and usage
2. **[Installation Guide](../README.md#installation-and-setup)** - Step-by-step setup for Linux, macOS, and Windows
3. **[Quick Start Examples](../README.md#quick-start)** - Get running in minutes

## Documentation Structure

### Core Documentation

- **[README.md](../README.md)** - Main project documentation
  - Project overview and scientific context
  - Installation instructions for all platforms
  - Usage examples and command-line interface
  - Data output specification
  - Repository structure

- **[DATA_DICTIONARY.md](../DATA_DICTIONARY.md)** - Complete data specification
  - Field-by-field descriptions
  - Data types and formats
  - Marker codes and timing information
  - Example data records

### Developer Resources

- **[API.md](API.md)** - Technical API reference
  - Module documentation
  - Function signatures and examples
  - Extension points for customization
  - Data structures and formats

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contributing guidelines
  - Development setup
  - Code style and standards
  - Testing procedures
  - Pull request process

### Support Documentation

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem-solving guide
  - Installation issues
  - Runtime problems
  - Platform-specific solutions
  - Performance optimization

- **[LICENSE](../LICENSE)** - Project license (MIT)

## Getting Started Paths

### For Researchers

If you want to **run experiments**:

1. [Installation Guide](../README.md#installation-and-setup) - Set up the environment
2. [Quick Start](../README.md#quick-start) - Run your first experiment
3. [Command-Line Interface](../README.md#command-line-interface) - Customize parameters
4. [Data Output](../README.md#data-output) - Understand your results
5. [Troubleshooting](TROUBLESHOOTING.md) - Solve common issues

### For Developers

If you want to **modify or extend** the task:

1. [Contributing Guidelines](../CONTRIBUTING.md) - Development setup
2. [API Reference](API.md) - Technical implementation details
3. [Repository Structure](../README.md#repository-structure) - Code organization
4. [Extension Points](API.md#extension-points) - Customization options

### For Data Analysts

If you want to **analyze N-back data**:

1. [Data Dictionary](../DATA_DICTIONARY.md) - Field specifications
2. [Data Output Format](../README.md#data-output) - File structure
3. [Example Data](../DATA_DICTIONARY.md#example-row) - Sample records
4. [Marker Codes](../DATA_DICTIONARY.md#marker-coding) - Event timing

## Key Features

### Scientific Validity

- **Precise timing** with display refresh rate detection
- **Validated sequence generation** with configurable constraints
- **Comprehensive data logging** for reproducible research
- **Cross-platform compatibility** for multi-site studies

### Technical Robustness

- **Frame-accurate stimulus presentation** using hardware vsync
- **Hardware keyboard support** for low-latency responses
- **Graceful error handling** with informative messages
- **Extensive configuration options** via command-line interface

### Research Integration

- **EEG/physiological markers** (LSL, Serial, Parallel port)
- **Customizable instruction text** for different populations
- **Practice phase with feedback** for participant training
- **Metadata export** for reproducibility and analysis

## Common Use Cases

### Basic Experiment

```bash
# Default two-load experiment (Version A: 1→3)
python nback_task.py --participant P001

# Quick pilot test (Version B, windowed, 1 block per load, 10 trials)
python nback_task.py --participant pilot --version B --windowed --blocks-per-load 1 --trials 10 --no-practice
```

### Research Configuration

```bash
# Version A with custom parameters
python nback_task.py --participant P001 --version A --blocks-per-load 4 --target-rate 0.4

# Reproducible experiment with seed
python nback_task.py --participant P001 --seed 1234
```

### Development and Testing

```bash
# Timing diagnostics
python scripts/timing_diagnostics.py --fullscr

# Sequence preview
PYTHONPATH=. python scripts/preview_seq.py 2 20
```

### Smoke Test

Run the built-in smoke test to validate the two-load design with minimal trials (windowed, no practice):

```bash
python scripts/smoke_test.py
```

## Support and Community

### Getting Help

1. **Check documentation first**: Most questions are answered here
2. **Search existing issues**: Someone may have faced the same problem
3. **Run diagnostics**: Use built-in tools to identify issues
4. **Report bugs**: Open GitHub issues with detailed information

### Contributing

We welcome contributions from the research community:

- **Bug reports** and fixes
- **Feature enhancements** for research needs
- **Documentation improvements**
- **Cross-platform testing**
- **Performance optimizations**

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

### Citation

If you use this implementation in your research, please cite appropriately (see [README.md](../README.md#citation) for citation format).

## Version Information

- **Current Version**: 1.0.0
- **PsychoPy Version**: 2025.1.1
- **Python Requirement**: 3.10.x
- **Last Updated**: August 2025

---

**Need immediate help?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or search [existing GitHub issues](https://github.com/TH3PL4Y3R1/n_back/issues).
