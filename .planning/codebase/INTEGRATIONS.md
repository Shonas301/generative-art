# External Integrations

**Analysis Date:** 2026-01-20

## APIs & External Services

**None:**
- this is a standalone generative art project
- no external API calls
- no network dependencies at runtime

## Data Storage

**Databases:**
- None - no database usage

**File Storage:**
- local filesystem only
- output images saved to `output/` directory
- bump maps loaded from local image files

**Caching:**
- None - no caching layer

## Authentication & Identity

**Auth Provider:**
- None - no authentication required
- standalone desktop application

## Monitoring & Observability

**Error Tracking:**
- None - errors print to console

**Logs:**
- console output via print statements
- click.echo for CLI feedback

## CI/CD & Deployment

**Hosting:**
- local development only
- no deployment infrastructure

**CI Pipeline:**
- None detected
- quality checks available: `ruff check . && mypy src && pytest`

## Environment Configuration

**Required env vars:**
- None - no environment variables used

**Secrets location:**
- None - no secrets required

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## External Tool Integrations

**Autodesk Maya:**
- `src/maya_grass/` package integrates with Maya
- conditional imports handle maya availability:
  ```python
  try:
      from maya import cmds
      MAYA_AVAILABLE = True
  except ImportError:
      MAYA_AVAILABLE = False
  ```
- modules work standalone for testing without Maya
- MASH API used for grass instancing: `import MASH.api as mapi`

**Integration points:**
- `maya_grass.generator.GrassGenerator` - main entry point
- `maya_grass.terrain.TerrainAnalyzer` - mesh analysis
- `maya_grass.wind.WindField` - wind simulation

**Data exchange formats:**
- JSON export/import for obstacles and grass points
- CSV export for external tool compatibility

## File Format Support

**Input:**
- grayscale images (PNG, JPG, etc.) via Pillow for bump maps
- JSON files for obstacle/point data

**Output:**
- PNG images for rendered sketches
- JSON files for data export
- CSV files for external tool compatibility

## Processing/Java Integration

**py5 Framework:**
- wraps Processing (Java-based graphics framework)
- requires JRE at runtime
- provides Sketch class pattern for graphics
- filter effects (BLUR) via Processing

**Usage pattern:**
```python
from py5 import Sketch

class MySketch(Sketch):
    def settings(self): self.size(width, height)
    def setup(self): self.background(color)
    def draw(self): # drawing code
```

---

*Integration audit: 2026-01-20*
