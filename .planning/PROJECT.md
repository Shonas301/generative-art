# Maya Grass Plugin

## What This Is

A Maya plugin for realistic procedural grass placement and animation. Users import the module in Maya's script editor, provide a terrain mesh and grass geometry, and generate thousands of animated grass instances with wind-driven movement.

## Core Value

Grass animates naturally in the wind and renders correctly — both in viewport preview and final render.

## Requirements

### Validated

- ✓ GrassGenerator class for MASH-based grass instancing — existing
- ✓ TerrainAnalyzer for mesh surface analysis and bump maps — existing
- ✓ WindField for Perlin noise-based wind simulation — existing
- ✓ Point clustering with obstacle avoidance — existing
- ✓ JSON/CSV export for grass point data — existing

### Active

- [ ] Replace `noise` library with `opensimplex` (pure Python, Windows-compatible)
- [ ] Update WindField to use opensimplex for organic wind patterns
- [ ] Update any flow field code that depends on `noise`
- [ ] Single cohesive entry point for Maya script import
- [ ] Verify animated wind works in Maya viewport
- [ ] Verify animation renders correctly in playblast/render

### Out of Scope

- py5 sketch integration — this milestone focuses only on maya_grass module
- GUI/panel interface — script import workflow is sufficient
- Cross-DCC support — Maya only for now

## Context

**Current state:**
- maya_grass module exists with GrassGenerator, TerrainAnalyzer, WindField
- Uses `noise` library which has C compilation issues on Windows
- Entry point exists via `from maya_grass import GrassGenerator` but needs verification

**Target workflow:**
```python
from maya_grass import GrassGenerator

gen = GrassGenerator()
gen.terrain.set_from_mesh("groundPlane")
gen.generate_points(count=5000)
gen.create_mash_network("grassBlade_geo")
```

**Technical environment:**
- Maya with Python 3.x
- MASH for instancing
- opensimplex as noise replacement (pure Python, pip-installable)

## Constraints

- **Platform**: Must work on Windows (no C compilation during pip install)
- **Dependencies**: opensimplex instead of noise for Windows compatibility
- **Maya version**: Python 3.x Maya (2022+)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| opensimplex over numpy-based noise | Active maintenance, pure Python, near-identical API to noise library | — Pending |
| Script import over GUI | User requested; simpler to implement and maintain | — Pending |

---
*Last updated: 2026-01-20 after initialization*
