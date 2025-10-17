# Contributing to N-back Task

Thank you for your interest in contributing to this N-back task implementation! We welcome contributions from the research community to improve and extend this tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for all contributors:

- Be respectful and inclusive in all interactions
- Focus on constructive feedback and collaboration
- Respect different perspectives and experience levels
- Help create a positive learning environment

## Getting Started

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Corrections to existing functionality
- **Feature enhancements**: New capabilities that align with the project's goals
- **Documentation improvements**: Better explanations, examples, or corrections
- **Performance optimizations**: Improvements to timing precision or efficiency
- **Test additions**: New tests that improve code coverage or reliability
- **Cross-platform compatibility**: Fixes for platform-specific issues

### Areas of Interest

Particularly valuable contributions include:

- Improved timing precision and validation
- Additional marker/trigger integrations
- Enhanced sequence generation algorithms
- Better cross-platform compatibility
- Performance optimizations
- User experience improvements
- Documentation enhancements

## Development Setup

### Prerequisites

- Python 3.10.x (required by PsychoPy)
- Git for version control
- Basic familiarity with PsychoPy framework

### Initial Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/n_back.git
   cd n_back
   ```

3. **Set up development environment**:
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   
   # Install dependencies
   pip install -U pip setuptools wheel
   pip install -r requirements.txt
   
   # Verify installation
   python check_psychopy.py
   ```

4. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/TH3PL4Y3R1/n_back.git
   ```

### Development Environment

#### Optional Development Tools

Consider installing these tools for better development experience:

```bash
# Code formatting and linting
pip install black flake8 isort mypy

# Testing framework (if adding tests)
pip install pytest pytest-cov
```

#### Editor Configuration

For consistent code formatting, consider using:
- **VS Code**: Install Python extension with Black formatter
- **PyCharm**: Configure Black as external tool
- **Other editors**: Configure to use Black with line length 88

## Contributing Guidelines

### Before You Start

1. **Check existing issues** to see if your bug/feature is already being worked on
2. **Open an issue** to discuss significant changes before implementing
3. **Keep changes focused** - one issue per pull request
4. **Write clear commit messages** describing what and why

### Branching Strategy

- **main branch**: Stable, released code
- **feature branches**: New features (`feature/description`)
- **bugfix branches**: Bug fixes (`bugfix/description`)
- **documentation branches**: Documentation updates (`docs/description`)

Example:
```bash
git checkout -b feature/improved-timing-validation
```

### Commit Messages

Use clear, descriptive commit messages:

```
Format: [type]: Brief description

Examples:
feat: Add support for parallel port markers
fix: Correct ITI calculation in sequence generation
docs: Update installation instructions for Windows
test: Add unit tests for sequence validation
refactor: Simplify marker sending logic
```

## Code Style

### Python Style Guide

Follow PEP 8 with these specific guidelines:

- **Line length**: 88 characters (Black default)
- **Imports**: Group and sort using isort
- **Type hints**: Use for function parameters and returns
- **Docstrings**: Use Google style for functions and classes

### Code Formatting

Use Black for automatic formatting:
```bash
black nback_task.py nback/ scripts/
```

Use isort for import sorting:
```bash
isort nback_task.py nback/ scripts/
```

### Documentation Style

- **Comments**: Explain why, not what
- **Docstrings**: Include parameters, returns, and examples
- **README updates**: Keep examples current and accurate
- **Type hints**: Use for better code clarity

### Example Code Style

```python
from typing import Optional, List
import logging

def generate_sequence(
    n_back: int, 
    n_trials: int, 
    target_rate: float = 0.3,
    seed: Optional[int] = None
) -> List[str]:
    """Generate N-back sequence with specified parameters.
    
    Args:
        n_back: N-back level (1, 2, or 3)
        n_trials: Number of trials to generate
        target_rate: Proportion of target trials (0.0-1.0)
        seed: Random seed for reproducibility
    
    Returns:
        List of stimulus letters
        
    Raises:
        ValueError: If parameters are invalid
    """
    # Implementation here
    pass
```

## Testing

### Running Tests

Currently, testing is primarily manual through the provided verification scripts:

```bash
# Verify PsychoPy installation
python check_psychopy.py

# Test timing performance
python scripts/timing_diagnostics.py --fullscr

# Validate sequence generation
python scripts/local_sequence_check.py

# Preview sequences
PYTHONPATH=. python scripts/preview_seq.py 2 10
```

### Test Your Changes

Before submitting:

1. **Test basic functionality**:
   ```bash
   # Quick test run
   python nback_task.py --participant test --windowed --version A --blocks-per-load 1 --trials 5 --no-practice
   ```

2. **Test cross-platform compatibility** (if possible):
   - Test on different operating systems
   - Verify with different Python 3.10.x versions

3. **Test edge cases**:
   - Invalid parameters
   - Missing files
   - Different screen resolutions/refresh rates

### Adding Tests

If adding formal tests (encouraged for complex changes):

```python
# tests/test_sequences.py
import pytest
from nback.sequences import generate_sequence

def test_sequence_length():
    """Test that sequence has correct length."""
    seq = generate_sequence(n_back=2, n_trials=10)
    assert len(seq) == 10

def test_target_rate():
    """Test that target rate is approximately correct."""
    seq = generate_sequence(n_back=2, n_trials=100, target_rate=0.3, seed=123)
    # Implementation to verify target rate
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test thoroughly** using the manual testing procedures above

3. **Update documentation** if your changes affect:
   - Command-line interface
   - Configuration options
   - Output format
   - Installation procedure

### Pull Request Template

When opening a pull request, include:

**Description**:
- Clear description of changes
- Motivation/reasoning for changes
- Any breaking changes

**Testing**:
- How you tested the changes
- Platforms tested on
- Any remaining concerns

**Checklist**:
- [ ] Code follows project style guidelines
- [ ] Changes have been tested manually
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)

### Review Process

1. **Automated checks**: Ensure any CI checks pass
2. **Code review**: Maintainers will review for quality and compatibility
3. **Testing**: Changes may be tested on different platforms
4. **Approval**: Maintainer approval required before merge

## Bug Reports

### Before Reporting

1. **Search existing issues** for similar problems
2. **Try latest version** to see if already fixed
3. **Test with minimal example** to isolate the issue

### Bug Report Template

Include the following information:

**Environment**:
- Operating system and version
- Python version
- PsychoPy version
- Hardware specifications (especially for timing issues)

**Steps to Reproduce**:
1. Exact command or steps taken
2. Expected behavior
3. Actual behavior

**Additional Information**:
- Error messages (full traceback)
- Log output
- Screenshots if relevant
- Minimal reproducible example

### Example Bug Report

```markdown
**Bug Description**: Task crashes when using custom ITI range

**Environment**:
- OS: Ubuntu 22.04
- Python: 3.10.8
- PsychoPy: 2025.1.1

**Steps to Reproduce**:
1. Run: `python nback_task.py --participant test --iti-min 100 --iti-max 200`
2. Task starts normally
3. Crashes during first trial with TypeError

**Error Message**:
```
Traceback (most recent call last):
  File "nback_task.py", line 123, in run_trial
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

**Expected**: Task should run with custom ITI range
**Actual**: Task crashes with type error
```

## Feature Requests

### Guidelines for Feature Requests

1. **Research relevance**: Features should serve research needs
2. **Backward compatibility**: Avoid breaking existing functionality
3. **Maintainability**: Consider long-term maintenance burden
4. **Scope**: Keep features focused and well-defined

### Feature Request Template

**Feature Description**:
- Clear description of proposed feature
- Research use case or motivation
- How it benefits the research community

**Implementation Ideas**:
- Suggested approach (if any)
- Potential challenges
- Alternative solutions considered

**Examples**:
- Sample usage or configuration
- Expected behavior

## Development Best Practices

### Code Organization

- **Modular design**: Keep functions focused and reusable
- **Clear interfaces**: Use type hints and docstrings
- **Error handling**: Provide helpful error messages
- **Configuration**: Make behavior configurable when appropriate

### Performance Considerations

- **Timing precision**: Maintain frame-accurate timing
- **Memory usage**: Avoid memory leaks in long experiments
- **Platform optimization**: Consider platform-specific optimizations

### Documentation

- **Code comments**: Explain complex algorithms or timing-critical sections
- **User documentation**: Update README and examples for new features
- **API documentation**: Document public functions and classes

## Questions?

If you have questions about contributing:

1. **Check existing documentation** in README.md and this file
2. **Search closed issues** for similar questions
3. **Open a new issue** with the "question" label
4. **Contact maintainers** if needed

Thank you for contributing to the N-back task implementation!