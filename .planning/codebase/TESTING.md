# Testing Patterns

**Analysis Date:** 2026-01-20

## Test Framework

**Runner:**
- pytest (version not pinned in requirements-dev.in)
- Config: `pyproject.toml` section `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest native assertions (no additional assertion library)

**Run Commands:**
```zsh
pytest                              # run all tests
pytest -vv                          # verbose output (configured by default)
pytest --cov=src --cov-report=term-missing  # with coverage
pytest tests/unit/                  # run only unit tests
pytest -k "test_parse"              # run tests matching pattern
```

**Configuration (`pyproject.toml`):**
```toml
[tool.pytest.ini_options]
addopts = "-vv --doctest-modules --doctest-report ndiff"
doctest_optionflags = "NORMALIZE_WHITESPACE IGNORE_EXCEPTION_DETAIL ELLIPSIS NUMBER"
testpaths = ["tests"]
markers = ["e2e"]
```

## Test File Organization

**Location:**
- Separate `tests/` directory at project root
- Subdirectories by test type: `unit/`, `integration/`, `system/`

**Naming:**
- Test files: `test_<module_name>.py`
- Test functions: `test_<what>_<condition>()` or `test_<method>_<behavior>()`

**Structure:**
```
tests/
├── unit/
│   ├── test_flow_field.py           # tests for flow_field.py
│   ├── test_incandescent_perlin_flow.py
│   ├── test_animated_incandescent_perlin_flow.py
│   └── test_maya_grass.py
├── integration/
│   └── dummy_test.py                # placeholder (empty)
└── system/
    └── (empty)
```

## Test Structure

**Suite Organization:**
Tests are organized by class under test using test classes:

```python
"""Unit tests for flow_field module."""

import math

import numpy as np
import pytest

from generative_art.flow_field import (
    ClusteringConfig,
    FlowField,
    FlowFieldConfig,
    Obstacle,
)


class TestObstacle:
    """Tests for Obstacle dataclass."""

    def test_obstacle_default_influence_radius(self) -> None:
        """test that default influence radius is 2.5x obstacle radius."""
        # given
        obstacle = Obstacle(x=100, y=100, radius=40)

        # then
        assert obstacle.influence_radius == 100.0


class TestFlowField:
    """Tests for FlowField class."""

    def test_flow_field_initialization_with_defaults(self) -> None:
        """test that flow field initializes with default config."""
        # given/when
        flow_field = FlowField()

        # then
        assert flow_field.config is not None
```

**Patterns:**
- **Given-When-Then comments:** Tests use `# given`, `# when`, `# then` comments to structure AAA pattern
- **Test class per production class:** `TestObstacle`, `TestFlowField`, `TestPointClusterer`
- **Descriptive docstrings:** Each test has a lowercase docstring explaining intent

## Mocking

**Framework:** Not heavily used; tests focus on real implementations

**Current patterns:**
- No mocks observed in existing tests
- Tests use real class instances with controlled inputs
- Seed-based reproducibility for random operations:
  ```python
  def test_seeded_generation_is_reproducible(self) -> None:
      """test that same seed produces same points."""
      # given
      clusterer1 = PointClusterer(width=1000, height=1000, seed=42)
      clusterer2 = PointClusterer(width=1000, height=1000, seed=42)

      # when
      points1 = clusterer1.generate_points_grid_based(50)
      points2 = clusterer2.generate_points_grid_based(50)

      # then
      assert points1 == points2
  ```

**What to Mock (if needed):**
- External services (none currently)
- File system operations for render tests
- py5/Processing graphics calls (not currently tested)

**What NOT to Mock:**
- Pure functions (test with real inputs)
- Dataclasses (test actual behavior)
- Noise functions (use seeded values for reproducibility)

## Fixtures and Factories

**Test Data:**
Direct instantiation in tests with explicit parameters:

```python
def test_add_obstacle(self) -> None:
    """test that obstacles can be added."""
    # given
    flow_field = FlowField()
    obstacle = Obstacle(x=100, y=100, radius=50)

    # when
    flow_field.add_obstacle(obstacle)

    # then
    assert len(flow_field.obstacles) == 1
    assert flow_field.obstacles[0] == obstacle
```

**Location:**
- No separate fixtures file; test data created inline
- Complex scenarios use local helper setup within test class

**Factory pattern for configs:**
```python
config = FlowFieldConfig(
    noise_scale=0.01,
    flow_strength=5.0,
    octaves=4,
)
```

## Coverage

**Requirements:**
- No enforced coverage threshold
- Coverage reports available via pytest-cov

**Configuration (`pyproject.toml`):**
```toml
[tool.coverage.run]
omit = [
    ".venv/*",
    "tests/*",
    "docs/*",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self\\.debug",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

**View Coverage:**
```zsh
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html  # generates htmlcov/
```

## Test Types

**Unit Tests (`tests/unit/`):**
- Test individual functions and classes in isolation
- Focus on pure logic (parsing, calculations, data structures)
- Currently covers: `parse_resolution()`, `FlowField`, `PointClusterer`, `Obstacle`, config dataclasses

**Integration Tests (`tests/integration/`):**
- Currently empty (placeholder `dummy_test.py`)
- Would test: multi-module interactions, CLI end-to-end

**System/E2E Tests (`tests/system/`):**
- Currently empty
- Would test: full sketch rendering, file output verification
- Marker configured: `markers = ["e2e"]`

## Common Patterns

**Async Testing:**
Not applicable - codebase is synchronous.

**Error Testing:**
```python
def test_parse_resolution_raises_error_for_invalid_string(self) -> None:
    """test that invalid resolution string raises ValueError."""
    # given
    invalid_resolution = "invalid"

    # when/then
    with pytest.raises(ValueError) as exc_info:
        parse_resolution(invalid_resolution)

    # then
    assert "invalid resolution: 'invalid'" in str(exc_info.value)
    assert "use shorthand" in str(exc_info.value)
```

**Boundary Testing:**
```python
def test_parse_resolution_raises_error_for_zero_dimensions(self) -> None:
    """test that zero dimensions raise ValueError."""
    # given
    zero_resolution = "0x0"

    # when/then
    with pytest.raises(ValueError):
        parse_resolution(zero_resolution)
```

**Floating Point Comparisons:**
```python
def test_get_base_flow_has_reasonable_magnitude(self) -> None:
    """test that base flow magnitude is within expected bounds."""
    # given
    config = FlowFieldConfig(flow_strength=2.0)
    flow_field = FlowField(config=config)

    # when
    vx, vy = flow_field.get_base_flow(100, 100)
    magnitude = math.sqrt(vx**2 + vy**2)

    # then - magnitude should be close to flow_strength
    assert 0 < magnitude <= config.flow_strength * 1.1
```

**Testing Probabilistic Code:**
```python
def test_generate_points_returns_requested_count(self) -> None:
    """test that generate_points returns approximately the requested count."""
    # given
    clusterer = PointClusterer(width=1000, height=1000, seed=42)

    # when
    points = clusterer.generate_points(100)

    # then - may not get exact count due to rejection sampling
    assert len(points) > 50  # should get reasonable number
    assert len(points) <= 100
```

## What Is Tested

**Currently tested:**
- `parse_resolution()` function (shorthand and WxH formats, error cases)
- `Obstacle` dataclass (defaults, custom values)
- `FlowFieldConfig` dataclass (defaults, custom values)
- `FlowField` class (initialization, obstacle management, flow calculations)
- `ClusteringConfig` dataclass
- `PointClusterer` class (density, point validity, generation)
- Convenience functions (`create_flow_field_with_obstacles`, `create_clustered_points`)

**Not currently tested:**
- Sketch classes (`RotatingFractals`, `NoiseFlowField`, etc.) - require py5 runtime
- CLI commands (Click integration)
- Actual image rendering and file output
- Animation frame generation

## Adding New Tests

**For new utility functions:**
1. Create test file in `tests/unit/test_<module>.py`
2. Use test class if testing a class: `class Test<ClassName>:`
3. Include `# given`, `# when`, `# then` comments
4. Add descriptive lowercase docstring
5. Test happy path, edge cases, and error conditions

**Test file template:**
```python
"""Unit tests for <module> module."""

import pytest

from generative_art.<module> import <Class>, <function>


class Test<Class>:
    """Tests for <Class>."""

    def test_<method>_<behavior>(self) -> None:
        """test that <expected behavior>."""
        # given
        instance = <Class>(...)

        # when
        result = instance.<method>(...)

        # then
        assert result == expected
```

---

*Testing analysis: 2026-01-20*
