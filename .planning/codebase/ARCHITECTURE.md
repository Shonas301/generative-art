# Architecture

**Analysis Date:** 2026-01-20

## Pattern Overview

**Overall:** Sketch-based Generative Art System with Shared Utilities

**Key Characteristics:**
- Self-contained sketches that extend py5.Sketch base class
- Shared utility modules for common operations (flow fields, export)
- CLI integration via click for sketch execution modes
- Dual-target output: py5 visualization and Maya 3D integration

## Layers

**Sketch Layer (Entry Points):**
- Purpose: Individual generative art pieces that can run standalone
- Location: `src/generative_art/*.py` (named sketches), `examples/01_pattern_iteration/*.py`
- Contains: Sketch classes extending py5.Sketch, CLI commands, render functions
- Depends on: Core utilities (flow_field, export), py5, noise
- Used by: End users via CLI or direct execution

**Core Utilities Layer:**
- Purpose: Reusable algorithms and infrastructure shared across sketches
- Location: `src/generative_art/flow_field.py`, `src/generative_art/export.py`
- Contains: FlowField, PointClusterer, ResolutionConfig, export functions
- Depends on: numpy, noise (pnoise)
- Used by: Sketch layer, Maya integration layer

**Maya Integration Layer:**
- Purpose: Bridge generative algorithms to Autodesk Maya for 3D grass animation
- Location: `src/maya_grass/`
- Contains: GrassGenerator, TerrainAnalyzer, WindField
- Depends on: Core utilities (flow_field), maya.cmds (optional)
- Used by: Maya scripts via python import

## Data Flow

**Static Image Render:**

1. User runs sketch with `--render` flag or `python sketch.py --render`
2. Sketch class instantiated with output_path
3. `settings()` configures canvas dimensions
4. `setup()` initializes background, parameters, calls `no_loop()`
5. `draw()` executes once, generates art, saves to output_path
6. `exit_sketch()` terminates py5 JVM

**Animation Frame Render:**

1. User runs sketch with `--render-animation` flag
2. Sequential renderer subclass created with frame counter
3. `draw()` called per frame, saves numbered frame, increments time_offset
4. Loop until frame count reached
5. User instructed to compile with ffmpeg

**Interactive Preview:**

1. User runs sketch without flags
2. Sketch instantiated without output_path
3. `setup()` does NOT call `no_loop()`
4. `draw()` called continuously at display framerate
5. Window closed by user to exit

**State Management:**
- Sketches store state as instance variables (particles, time_offset, etc.)
- No external state persistence - each run is independent
- Random seeds available for reproducibility (`--seed` flag)

## Key Abstractions

**py5.Sketch Base Class:**
- Purpose: Processing-style graphics framework for Python
- Examples: `RotatingFractals`, `IncandesceeentPerlinFlow`, `FluffyClouds`
- Pattern: Override `settings()`, `setup()`, `draw()` methods

**FlowField:**
- Purpose: Perlin noise-based vector field with obstacle avoidance
- Examples: `src/generative_art/flow_field.py`
- Pattern: Composition with config dataclasses, obstacle list

**PointClusterer:**
- Purpose: Generate point distributions with density modulation around obstacles
- Examples: `src/generative_art/flow_field.py`
- Pattern: Rejection sampling with configurable density function

**ResolutionConfig:**
- Purpose: Standard output dimensions (4K, 1080p, QHD portrait)
- Examples: `src/generative_art/export.py`
- Pattern: Class attributes as named constants

## Entry Points

**CLI via `__main__.py`:**
- Location: `src/generative_art/__main__.py`
- Triggers: `python -m generative_art <command>`
- Responsibilities: Route to specific sketch commands (perlin, animated-perlin)

**Direct Sketch Execution:**
- Location: Each sketch file (e.g., `src/generative_art/incandescent_perlin_flow.py`)
- Triggers: `python <sketch>.py` or `python <sketch>.py --render`
- Responsibilities: Parse CLI args, instantiate sketch, run preview or render

**Example Sketches:**
- Location: `examples/01_pattern_iteration/*.py`
- Triggers: Direct python execution
- Responsibilities: Self-contained demonstrations of techniques

**Maya Integration:**
- Location: `src/maya_grass/__init__.py`
- Triggers: `from maya_grass import GrassGenerator` in Maya script editor
- Responsibilities: Expose terrain analysis, wind fields, grass generation to Maya

## Error Handling

**Strategy:** Fail-fast with descriptive messages

**Patterns:**
- Resolution parsing raises `ValueError` with format guidance
- click.Abort() for CLI argument validation failures
- Maya module imports wrapped in try/except with fallback flags (`MAYA_AVAILABLE`)
- No silent failures - errors printed to console

## Cross-Cutting Concerns

**Logging:** Console output via `print()` and `click.echo()` for user feedback during render progress

**Validation:** Resolution string parsing validates format and positive dimensions; obstacles check boundaries

**Configuration:** Dataclasses for typed configuration (FlowFieldConfig, ClusteringConfig, Obstacle); CLI options via click decorators

---

*Architecture analysis: 2026-01-20*
