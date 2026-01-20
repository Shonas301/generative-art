# Coding Conventions

**Analysis Date:** 2026-01-20

## Naming Patterns

**Files:**
- snake_case for all Python files (e.g., `incandescent_perlin_flow.py`, `flow_field.py`)
- Descriptive names reflecting the visual effect or algorithm (e.g., `fluffy_clouds.py`, `rotating_fractals.py`)
- Test files prefixed with `test_` (e.g., `test_flow_field.py`)

**Functions:**
- snake_case for all functions (e.g., `draw_flow_line`, `parse_resolution`, `get_density_at`)
- Verb-first naming for actions (e.g., `render_all_resolutions`, `create_clustered_points`)
- Use `get_` prefix for accessor methods (e.g., `get_base_flow`, `get_flow_angle`)

**Variables:**
- snake_case for all variables (e.g., `canvas_width`, `num_particles`, `noise_scale`)
- Descriptive names with units where relevant (e.g., `flow_strength`, `time_offset`)
- Single-letter variables only for loop indices or coordinates (`x`, `y`, `i`)

**Classes:**
- PascalCase for class names (e.g., `RotatingFractals`, `FlowField`, `PointClusterer`)
- Sketch classes named after the visual effect (e.g., `FluffyClouds`, `GeometricSpiral`)
- Config dataclasses suffixed with `Config` (e.g., `FlowFieldConfig`, `ClusteringConfig`)

**Types:**
- PascalCase for type aliases and dataclasses
- Union types use `|` syntax (e.g., `str | None`, `FlowFieldConfig | None`)

## Code Style

**Formatting:**
- Ruff configured in `pyproject.toml`
- Line length: 88 characters (Black-compatible)
- Target Python 3.12+

**Linting:**
- Ruff with extensive rule set enabled
- Key rules: E, F, W, I (isort), D (docstrings), B, N, PT, RUF
- Google-style docstrings enforced (`convention = "google"`)
- Max complexity: 10 (mccabe)

**Per-file ignores in `pyproject.toml`:**
```python
# tests don't require docstrings
"tests/*" = ["D", "INP001"]
# flow sketches can use print() for user feedback
"src/generative_art/*_flow*.py" = ["T201", "FBT001", "FBT002", "PLR0913"]
# CLI entry points have boolean args from click decorators
"src/generative_art/__main__.py" = ["FBT001", "T201"]
```

## Import Organization

**Order (enforced by isort via Ruff):**
1. Standard library imports (`from pathlib import Path`, `import math`)
2. Third-party imports (`import click`, `from noise import pnoise2`, `from py5 import Sketch`)
3. First-party imports (`from generative_art.export import ResolutionConfig`)

**Path Aliases:**
- None configured; use full relative imports within package
- Known first-party: `generative_art` (configured in `pyproject.toml`)

**Pattern:**
```python
"""Module docstring."""

from pathlib import Path

import click
import numpy as np
from noise import pnoise2
from py5 import Sketch

from generative_art.export import ResolutionConfig
```

## Error Handling

**Patterns:**
- Raise `ValueError` for invalid user input (e.g., resolution parsing)
- Use descriptive error messages with context:
  ```python
  msg = (
      f"invalid resolution: '{resolution_str}'. "
      f"use shorthand ({valid_formats}) or WIDTHxHEIGHT format"
  )
  raise ValueError(msg)
  ```
- Use `click.Abort()` for CLI errors after displaying message via `click.echo(..., err=True)`
- Pattern for CLI error handling:
  ```python
  try:
      resolution_tuple = parse_resolution(resolution)
  except ValueError as e:
      click.echo(f"error: {e}", err=True)
      raise click.Abort()
  ```

**No bare exceptions.** Always catch specific exception types.

## Logging

**Framework:** `print()` for user feedback in sketches; `click.echo()` for CLI output

**Patterns:**
- Use emoji for visual status (render mode): `"🎨 rendering..."`, `"✨ complete!"`
- Progress reporting format: `"frame 0042/0900 (4.7%) - 0.85 fps - eta: 02:15"`
- File save confirmation: `f"    Saved: {self.output_path}"`
- CLI mode indicators: preview vs render mode clearly stated

## Comments

**When to Comment:**
- Algorithm explanations for non-obvious math (noise calculations, transformations)
- Rationale for magic numbers when not self-evident
- Warning comments for platform-specific behavior (e.g., macOS JVM limitations)

**Comment style:**
- Lowercase comments as per user preference (unless referencing capitalized identifiers)
- Inline comments for clarification: `# 80, 160, 240, 320, 400 pixels`

**Docstrings (Google-style, enforced):**
```python
def draw_flow_line(self, start_pos: list[float], particle_id: int) -> None:
    """Draw a flowing line following the noise field.

    Args:
        start_pos: Starting [x, y] position
        particle_id: Unique particle identifier for color variation
    """
```

## Function Design

**Size:**
- Keep functions focused; aim for < 40 lines
- Complex algorithms (like Poisson disk sampling) can be longer but are isolated

**Parameters:**
- Use type hints for all parameters and return types
- Optional parameters use `| None` with default `None`
- Dataclass configs for grouped parameters (e.g., `FlowFieldConfig`, `ClusteringConfig`)

**Return Values:**
- Single values or tuples for simple returns: `tuple[float, float]`
- Use dataclasses for complex return structures
- Always specify return type, including `-> None` for void

## Module Design

**Exports:**
- Define `__all__` in `__init__.py` to explicitly export public API
- Example from `src/generative_art/__init__.py`:
  ```python
  __all__ = [
      "ClusteringConfig",
      "FlowField",
      "FlowFieldConfig",
      "Obstacle",
      ...
  ]
  ```

**Barrel Files:**
- `__init__.py` re-exports key classes and functions from submodules
- External code imports from package root: `from generative_art import FlowField`

## Type Hints

**Mandatory everywhere:**
- All function parameters must have type hints
- All return types must be specified (use `-> None` for void)
- Instance variables in `__init__` should be typed

**Modern syntax (Python 3.12+):**
- Use `list[type]` not `List[type]`
- Use `dict[str, int]` not `Dict[str, int]`
- Use `tuple[int, int]` not `Tuple[int, int]`
- Use `X | None` not `Optional[X]`

**MyPy configuration in `pyproject.toml`:**
```toml
[tool.mypy]
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
```

## Sketch Pattern

All py5 sketches follow this class structure:

```python
class SketchName(Sketch):
    """Docstring describing the visual effect."""

    def __init__(
        self, width: int = 1920, height: int = 1080, output_path: str | None = None
    ) -> None:
        """Initialize parameters."""
        super().__init__()
        self.canvas_width = width
        self.canvas_height = height
        self.output_path = output_path
        # sketch-specific parameters

    def settings(self) -> None:
        """Configure size and renderer."""
        self.size(self.canvas_width, self.canvas_height)

    def setup(self) -> None:
        """One-time setup."""
        self.background(...)
        self.no_loop()  # for static images (remove for animation)

    def draw(self) -> None:
        """Main drawing logic."""
        # drawing code
        if self.output_path:
            self.save(self.output_path)
            self.exit_sketch()
```

## CLI Pattern

Sketches with CLI use Click decorators:

```python
@click.command()
@click.option("--render", is_flag=True, help="render mode")
@click.option("--resolution", default="1080p", help="resolution shorthand or WxH")
@click.option("--output", default="output/name.png", help="output path")
def main(render: bool, resolution: str, output: str) -> None:
    """CLI entry point."""
    # parse and validate
    # dispatch to preview or render mode
```

---

*Convention analysis: 2026-01-20*
