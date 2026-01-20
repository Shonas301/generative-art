# Technology Stack

**Analysis Date:** 2026-01-20

## Languages

**Primary:**
- Python 3.12+ - all sketches, utilities, and maya plugins

**Secondary:**
- None - monolingual Python codebase

## Runtime

**Environment:**
- Python 3.13.0 (detected in .venv)
- Java Runtime Environment (required by py5/Processing)

**Package Manager:**
- pip with pip-tools for dependency management
- Lockfile: not present (uses requirements.in without compiled .txt)

## Frameworks

**Core:**
- py5 - Processing for Python, provides Sketch class for graphics rendering
- noise - Perlin noise generation (pnoise1, pnoise2, pnoise3)
- numpy - numerical operations for flow field calculations

**CLI:**
- click - command-line interface for sketch execution modes

**Testing:**
- pytest - test runner
- pytest-cov - coverage reporting
- pytest-mock - mocking utilities
- pytest-sugar - prettier test output

**Build/Dev:**
- ruff - linting and formatting (replaces black, flake8, isort)
- mypy - static type checking (strict mode)
- setuptools - package building

## Key Dependencies

**Critical:**
- `py5` - core graphics framework, wraps Processing/Java
- `noise` - perlin noise for organic patterns, essential for flow fields
- `numpy` - vector math, point clustering algorithms
- `pillow` - image loading for bump maps in terrain analysis

**Infrastructure:**
- `click` - CLI command handling for render/preview modes

**Maya Integration (conditional):**
- `maya.cmds` - maya command interface (imported conditionally)
- `maya.OpenMaya` - maya API (imported conditionally)
- `MASH.api` - maya MASH instancing (imported conditionally)

## Configuration

**Environment:**
- no .env files used
- no runtime secrets required
- java JRE must be installed (py5 dependency)

**Build:**
- `pyproject.toml` - tool configuration (ruff, mypy, pytest, coverage)
- `setup.py` - package setup with dynamic requirements loading
- `requirements.in` - production dependencies
- `requirements-dev.in` - development dependencies

**Key pyproject.toml settings:**
- `target-version = "py312"` - Python 3.12 target
- `line-length = 88` - matches Black style
- `convention = "google"` - Google-style docstrings
- strict mypy: `disallow_untyped_defs = true`, `disallow_incomplete_defs = true`

## Platform Requirements

**Development:**
- macOS (darwin detected, but should work cross-platform)
- Python 3.12+
- Java Runtime Environment for py5
- virtual environment recommended (`.venv/`)

**Production:**
- standalone - no deployment target
- sketches render to local `output/` directory
- maya plugin requires Autodesk Maya with Python 3.x

## Dependency Versions

**Note:** Version pinning is loose - `requirements.in` lists packages without versions:
```
py5
noise
numpy
pillow
click
```

Consider using `pip-compile` to generate `requirements.txt` with pinned versions for reproducibility.

---

*Stack analysis: 2026-01-20*
