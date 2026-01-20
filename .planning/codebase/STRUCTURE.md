# Codebase Structure

**Analysis Date:** 2026-01-20

## Directory Layout

```
generative-art/
├── src/
│   ├── generative_art/       # main package - sketches and utilities
│   │   ├── __init__.py       # package exports
│   │   ├── __main__.py       # CLI entry point
│   │   ├── export.py         # multi-resolution export utilities
│   │   ├── flow_field.py     # flow field + clustering algorithms
│   │   ├── incandescent_perlin_flow.py      # static perlin flow sketch
│   │   ├── animated_incandescent_perlin_flow.py  # animated version
│   │   ├── fluffy_clouds.py  # fBm cloud generator sketch
│   │   └── grass_flow_field.py  # interactive flow visualization
│   └── maya_grass/           # maya integration package
│       ├── __init__.py       # package exports
│       ├── generator.py      # main grass generation system
│       ├── terrain.py        # terrain/bump map analysis
│       └── wind.py           # wind field for maya
├── examples/
│   └── 01_pattern_iteration/ # standalone example sketches
│       ├── rotating_fractals.py
│       ├── noise_flow_field.py
│       ├── geometric_spiral.py
│       └── outputs/          # example outputs (gitignored)
├── tests/
│   ├── unit/                 # unit tests
│   ├── integration/          # integration tests
│   └── system/               # system tests (empty)
├── docs/                     # documentation
│   ├── algorithms.md         # algorithm explanations
│   └── maya-usage-guide.md   # maya plugin guide
├── output/                   # render outputs (gitignored)
│   ├── frames/               # animation frame sequences
│   └── temp_frames/          # temporary frame storage
├── .planning/                # GSD planning documents
│   └── codebase/             # codebase analysis docs
├── requirements.in           # production dependencies
├── requirements-dev.in       # development dependencies
├── pyproject.toml            # project config (ruff, mypy, pytest)
├── setup.py                  # package installation
├── CLAUDE.md                 # project instructions for Claude
└── README.md                 # project readme
```

## Directory Purposes

**`src/generative_art/`:**
- Purpose: Main Python package with sketches and shared utilities
- Contains: Sketch classes, CLI commands, export utilities, flow field algorithms
- Key files: `flow_field.py` (core algorithms), `export.py` (rendering utilities)

**`src/maya_grass/`:**
- Purpose: Maya plugin for procedural grass generation
- Contains: GrassGenerator, TerrainAnalyzer, WindField classes
- Key files: `generator.py` (main interface), `terrain.py` (bump map processing)

**`examples/01_pattern_iteration/`:**
- Purpose: Self-contained example sketches demonstrating techniques
- Contains: Complete standalone sketches that don't require package installation
- Key files: `rotating_fractals.py`, `geometric_spiral.py`, `noise_flow_field.py`

**`tests/`:**
- Purpose: Test suite organized by test type
- Contains: Unit tests for utility functions (resolution parsing, etc.)
- Key files: `tests/unit/test_incandescent_perlin_flow.py`

**`output/`:**
- Purpose: Generated render outputs (not version controlled)
- Contains: PNG images, frame sequences for animations
- Key files: Named by sketch and resolution (e.g., `perlin_flow_1080p.png`)

## Key File Locations

**Entry Points:**
- `src/generative_art/__main__.py`: CLI entry (`python -m generative_art`)
- `src/generative_art/incandescent_perlin_flow.py`: Perlin flow sketch with CLI
- `src/generative_art/animated_incandescent_perlin_flow.py`: Animated perlin with CLI
- `examples/01_pattern_iteration/*.py`: Standalone sketch entry points

**Configuration:**
- `pyproject.toml`: Ruff, mypy, pytest configuration
- `setup.py`: Package metadata and dependencies
- `requirements.in`: Production dependencies (py5, noise, numpy, pillow)
- `requirements-dev.in`: Dev dependencies (ruff, mypy, pytest)

**Core Logic:**
- `src/generative_art/flow_field.py`: FlowField, Obstacle, PointClusterer classes
- `src/generative_art/export.py`: ResolutionConfig, export_multi_resolution()
- `src/maya_grass/generator.py`: GrassGenerator, GrassPoint classes
- `src/maya_grass/terrain.py`: TerrainAnalyzer for bump map processing

**Testing:**
- `tests/unit/test_incandescent_perlin_flow.py`: Resolution parsing tests
- `tests/unit/test_animated_incandescent_perlin_flow.py`: Animated variant tests
- `tests/integration/dummy_test.py`: Placeholder integration test

## Naming Conventions

**Files:**
- snake_case for all Python files: `incandescent_perlin_flow.py`
- Descriptive names indicating sketch content: `rotating_fractals.py`, `fluffy_clouds.py`
- Test files prefixed with `test_`: `test_incandescent_perlin_flow.py`

**Directories:**
- snake_case for packages: `generative_art`, `maya_grass`
- Numbered prefixes for example categories: `01_pattern_iteration`

**Classes:**
- PascalCase: `RotatingFractals`, `FlowField`, `GrassGenerator`
- Sketch classes named for their visual output: `IncandesceeentPerlinFlow`

**Functions:**
- snake_case: `render_all_resolutions()`, `parse_resolution()`, `get_flow()`
- CLI entry points named `main()`

## Where to Add New Code

**New Sketch:**
- Primary code: `src/generative_art/<sketch_name>.py`
- Follow pattern: class extending py5.Sketch with settings/setup/draw methods
- Include CLI with click decorators for --render, --resolution, --output
- Tests: `tests/unit/test_<sketch_name>.py`

**New Example Sketch:**
- Implementation: `examples/<category>/<sketch_name>.py`
- Self-contained with own main() and render_all_resolutions()
- No package dependencies beyond installed generative_art

**New Utility/Algorithm:**
- Shared helpers: `src/generative_art/<utility_name>.py`
- Export from `src/generative_art/__init__.py`
- Add tests in `tests/unit/test_<utility_name>.py`

**New Maya Feature:**
- Implementation: `src/maya_grass/<feature>.py`
- Export from `src/maya_grass/__init__.py`
- Wrap maya imports in try/except for non-maya testing

**New CLI Command:**
- Add click command in source sketch file
- Register in `src/generative_art/__main__.py` via `cli.add_command()`

## Special Directories

**`output/`:**
- Purpose: Render output storage
- Generated: Yes, by sketch execution
- Committed: No (gitignored)

**`.planning/codebase/`:**
- Purpose: GSD codebase analysis documents
- Generated: Yes, by codebase mapping
- Committed: Varies by project policy

**`.venv/`:**
- Purpose: Python virtual environment
- Generated: Yes, by `python -m venv`
- Committed: No (gitignored)

**`src/generative_art.egg-info/`:**
- Purpose: Package metadata from editable install
- Generated: Yes, by `pip install -e .`
- Committed: No

---

*Structure analysis: 2026-01-20*
