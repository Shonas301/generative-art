# Codebase Concerns

**Analysis Date:** 2026-01-20

## Tech Debt

**Duplicated `parse_resolution()` function:**
- Issue: the `parse_resolution()` function is copy-pasted across 5 files with identical logic
- Files: `src/generative_art/incandescent_perlin_flow.py`, `src/generative_art/animated_incandescent_perlin_flow.py`, `src/generative_art/fluffy_clouds.py`, `src/generative_art/grass_flow_field.py`, `examples/01_pattern_iteration/` (implied by pattern)
- Impact: changes to resolution parsing logic must be made in multiple places; risk of divergence
- Fix approach: extract to shared utility module `src/generative_art/resolution.py` and import everywhere

**Duplicated `render_all_resolutions()` pattern:**
- Issue: each sketch file has its own implementation of multi-resolution rendering, duplicating the iteration logic
- Files: `src/generative_art/incandescent_perlin_flow.py`, `src/generative_art/fluffy_clouds.py`, all `examples/01_pattern_iteration/*.py` files
- Impact: inconsistent output directory naming (some use "outputs", some use "output", some use relative paths)
- Fix approach: use the existing `export.py` utilities consistently, or extend them to support all use cases

**Typo in class name:**
- Issue: class is named `IncandesceeentPerlinFlow` (extra 'e') instead of `IncandescentPerlinFlow`
- Files: `src/generative_art/incandescent_perlin_flow.py:17`, `src/generative_art/animated_incandescent_perlin_flow.py:17`
- Impact: minor; awkward public API, harder to type correctly
- Fix approach: rename class and update all references (breaking change for anyone importing directly)

**Empty Makefile:**
- Issue: Makefile exists but is empty (0 bytes)
- Files: `/Users/jasonshipp/code/generative-art/Makefile`
- Impact: no make commands available; documentation references to `make` commands would fail
- Fix approach: either populate with useful targets (test, lint, render) or delete

**Empty test directories:**
- Issue: `tests/system/` and `tests/integration/dummy_test.py` (empty) exist as scaffolding but have no real tests
- Files: `tests/system/` (empty directory), `tests/integration/dummy_test.py` (empty file)
- Impact: false sense of test coverage structure; system tests are not actually implemented
- Fix approach: add actual tests or remove empty scaffolding

**Inconsistent CLI patterns between sketches:**
- Issue: some sketches use click (`incandescent_perlin_flow.py`), some use `sys.argv` parsing (`rotating_fractals.py`)
- Files: `src/generative_art/` uses click, `examples/01_pattern_iteration/` uses manual argv
- Impact: inconsistent user experience, harder to maintain
- Fix approach: standardize on click for all runnable sketches

## Known Bugs

**JVM/OpenGL crashes on macOS during parallel rendering:**
- Symptoms: SIGILL crashes in AppKit NSWindow operations when running multiple py5 sketches
- Files: evidence in 12+ `hs_err_pid*.log` crash dumps at project root
- Trigger: attempting to run multiple py5 sketches in parallel (multiprocessing), especially with P2D/P3D renderers
- Workaround: use sequential rendering only (documented in `animated_incandescent_perlin_flow.py:246-256`)

**Export utility closure bug:**
- Symptoms: when using `export_multi_resolution()`, the `draw_and_save` closure may capture stale variables
- Files: `src/generative_art/export.py:59-66`
- Trigger: the closure captures `original_draw` and `output_file` in a loop, but Python closures capture by reference
- Workaround: likely works due to immediate execution, but pattern is fragile
- Fix approach: use `functools.partial` or default argument binding

## Security Considerations

**No file path sanitization:**
- Risk: output paths from CLI args are used directly without validation
- Files: all CLI entry points that accept `--output` parameter
- Current mitigation: none; paths are passed directly to `Path()` and `save()`
- Recommendations: validate paths don't contain `..`, restrict to allowed output directories

**Maya plugin conditional imports:**
- Risk: minimal; the try/except import pattern is appropriate for optional dependencies
- Files: `src/maya_grass/terrain.py:18-28`, `src/maya_grass/generator.py`, `src/maya_grass/wind.py`
- Current mitigation: graceful fallback to stub values when maya not available
- Recommendations: none needed; pattern is correct

## Performance Bottlenecks

**Fluffy clouds per-pixel rendering:**
- Problem: draws individual rectangles for each pixel position in nested loops
- Files: `src/generative_art/fluffy_clouds.py:70-81`
- Cause: O(width * height) draw calls, each involving stroke/fill state changes
- Improvement path: use pixel array manipulation via `load_pixels()`/`update_pixels()` or numpy

**Flow field redundant obstacle distance calculations:**
- Problem: obstacle deflection calculates distance for every flow query
- Files: `src/generative_art/flow_field.py:124-181`
- Cause: no spatial partitioning; iterates all obstacles for every point
- Improvement path: for large obstacle counts, use spatial hashing or quadtree

**Animated flow field per-frame recalculation:**
- Problem: draws 3000 particles x 250 steps = 750,000 line segments per frame
- Files: `src/generative_art/animated_incandescent_perlin_flow.py:88-170`
- Cause: inherent to the visualization approach
- Improvement path: reduce particle count for preview, use GPU shaders, or cache flow vectors

## Fragile Areas

**py5 sketch lifecycle:**
- Files: all sketch classes inheriting from `py5.Sketch`
- Why fragile: py5 has specific requirements about when settings/setup/draw are called, and JVM threading constraints
- Safe modification: always test with both preview mode and render mode; avoid manipulating sketch state outside lifecycle methods
- Test coverage: limited; only `parse_resolution` utility is tested, not actual sketch execution

**Export wrapper monkey-patching:**
- Files: `src/generative_art/export.py:59-66`
- Why fragile: replaces sketch's `draw` method at runtime
- Safe modification: test with multiple resolution exports; verify original draw is called exactly once
- Test coverage: none

**Maya API integration:**
- Files: `src/maya_grass/*.py`
- Why fragile: depends on Maya Python environment which can't be tested outside Maya
- Safe modification: maintain clear separation between pure Python logic (testable) and Maya API calls
- Test coverage: zero (maya modules can only be tested inside Maya)

## Scaling Limits

**Point clustering rejection sampling:**
- Current capacity: works well up to ~10,000 points
- Limit: O(n^2) collision detection; `max_attempts = num_points * 100` hard limit
- Scaling path: use spatial hashing for collision detection; switch to Poisson disk sampling with blue noise
- Files: `src/generative_art/flow_field.py:361-395`

**Animation frame rendering:**
- Current capacity: 900 frames (30 seconds) takes ~15-60 minutes depending on resolution
- Limit: sequential rendering only (JVM crash issue prevents parallelization)
- Scaling path: render on Linux where multiprocessing works; use GPU acceleration; pre-compute flow fields
- Files: `src/generative_art/animated_incandescent_perlin_flow.py:246-354`

## Dependencies at Risk

**py5 (Processing for Python):**
- Risk: depends on Java runtime; version compatibility issues with different JDK versions
- Impact: sketches won't run if JRE not installed or incompatible
- Migration plan: alternative would be pygame or cairo; significant rewrite required

**noise (Perlin noise):**
- Risk: unmaintained PyPI package; last update was years ago
- Impact: low; package is stable, just not actively maintained
- Migration plan: could use numpy-based perlin implementation or `opensimplex` package

## Missing Critical Features

**No test coverage for visual output:**
- Problem: no way to verify that rendered outputs are correct
- Blocks: confident refactoring; catching visual regressions
- Suggestion: add snapshot/golden image testing for key outputs

**No CI/CD pipeline:**
- Problem: no automated testing on push/PR
- Blocks: catching regressions before merge; ensuring cross-platform compatibility
- Suggestion: add GitHub Actions workflow for linting and testing

## Test Coverage Gaps

**Sketch classes entirely untested:**
- What's not tested: all Sketch subclasses (`RotatingFractals`, `NoiseFlowField`, `GeometricSpiral`, `IncandesceeentPerlinFlow`, etc.)
- Files: `src/generative_art/*.py`, `examples/01_pattern_iteration/*.py`
- Risk: changes to drawing logic could break output with no warning
- Priority: Medium - visual output is hard to test automatically

**Flow field module partially tested:**
- What's not tested: `FlowField`, `PointClusterer`, `Obstacle` classes and their interactions
- Files: `src/generative_art/flow_field.py` (536 lines, 0 test coverage)
- Risk: core algorithmic logic that affects all flow-based sketches
- Priority: High - this is pure Python logic that can and should be unit tested

**Maya grass module untested:**
- What's not tested: entire `src/maya_grass/` module (TerrainAnalyzer, WindField, GrassGenerator)
- Files: `src/maya_grass/terrain.py`, `src/maya_grass/wind.py`, `src/maya_grass/generator.py`
- Risk: Maya integration is complex and error-prone
- Priority: Medium - can test non-Maya-dependent logic outside Maya

**Only `parse_resolution` has tests:**
- What's tested: resolution string parsing in 2 test files with duplicate test cases
- Files: `tests/unit/test_incandescent_perlin_flow.py`, `tests/unit/test_animated_incandescent_perlin_flow.py`
- Risk: extremely narrow coverage (tests are also duplicated, adding maintenance burden)
- Priority: High - need broader coverage and DRY up test code

## Untracked Generated Files

**JVM crash logs polluting root directory:**
- Issue: 12+ `hs_err_pid*.log` files and `ffmpeg2pass-0.log` in project root
- Files: `/Users/jasonshipp/code/generative-art/hs_err_pid*.log`, `/Users/jasonshipp/code/generative-art/ffmpeg2pass-0.log`
- Impact: clutters repository; may accidentally get committed
- Fix approach: add `hs_err_pid*.log` and `ffmpeg*.log` to `.gitignore`; delete existing files

---

*Concerns audit: 2026-01-20*
