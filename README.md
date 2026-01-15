# Generative Art

A collection of generative art sketches created with Python, designed to produce visually interesting background pieces for portfolio websites and design projects.

## Overview

This project uses **py5** (Processing for Python) to create algorithmic art through:
- Pattern iteration and recursion
- Perlin noise for organic variation
- Geometric transforms (rotation, scaling, translation)
- Color gradients and layering
- Post-processing effects

## Setup

### Requirements

- Python 3.12+
- Java Runtime Environment (required for py5)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd generative-art
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.in
```

Or for development (includes linting, testing):
```bash
pip install -r requirements-dev.in
```

## Usage

### Running Examples

**Preview Mode** - View in a window:
```bash
cd examples/01_pattern_iteration
python rotating_fractals.py
```

**Render Mode** - Generate high-resolution outputs:
```bash
python rotating_fractals.py --render
```

This automatically generates three versions:
- **4K** (3840 x 2160) - Desktop/web backgrounds
- **1080p** (1920 x 1080) - Standard HD displays
- **QHD Portrait** (1440 x 2560) - Mobile phone screens

All outputs are saved to the `outputs/` directory as PNG files.

### Creating New Sketches

Basic py5 sketch structure:

```python
import py5
from noise import pnoise1

class MySketch:
    def __init__(self):
        self.width = 1920
        self.height = 1080

    def settings(self):
        py5.size(self.width, self.height)

    def setup(self):
        py5.background(255)
        py5.no_loop()

    def draw(self):
        # Your generative art code here
        pass

def main():
    sketch = MySketch()
    py5.run_sketch(py5_object=sketch)

if __name__ == "__main__":
    main()
```

### Rendering Multiple Resolutions

All example sketches support automatic multi-resolution rendering. To add this to your own sketches:

```python
from pathlib import Path
import py5

class MySketch:
    def __init__(self, width=1920, height=1080, output_path=None):
        self.width = width
        self.height = height
        self.output_path = output_path

    def draw(self):
        # Your drawing code here

        # Save if output path provided
        if self.output_path:
            py5.save(self.output_path)

def render_all_resolutions(output_dir="outputs"):
    resolutions = {
        "4k": (3840, 2160),
        "1080p": (1920, 1080),
        "qhd_portrait": (1440, 2560),
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for res_name, (width, height) in resolutions.items():
        output_file = output_path / f"my_sketch_{res_name}.png"
        sketch = MySketch(width=width, height=height, output_path=str(output_file))
        py5.run_sketch(py5_object=sketch)
```

## Examples

### 01_pattern_iteration

Three sketches demonstrating pattern iteration techniques:

1. **rotating_fractals.py** - Recursive fractal patterns with noise
2. **noise_flow_field.py** - Flowing particle system following noise field
3. **geometric_spiral.py** - Spiraling geometric shapes

See [examples/01_pattern_iteration/README.md](examples/01_pattern_iteration/README.md) for details.

## Development

This project includes:
- **Linting:** Ruff with Google-style docstrings
- **Type checking:** mypy with strict settings
- **Testing:** pytest with coverage

Run checks:
```bash
ruff check .
mypy src
pytest
```

## Project Structure

```
generative-art/
├── examples/           # Example sketches organized by technique
│   └── 01_pattern_iteration/
├── src/
│   └── generative_art/ # Reusable utilities and helpers
├── tests/              # Unit, integration, and system tests
├── requirements.in     # Production dependencies
└── requirements-dev.in # Development dependencies
```

## Tips for Portfolio Backgrounds

- Use the **--render flag** to generate all resolutions at once
- **4K output** provides crisp quality for high-DPI displays
- **QHD portrait** is perfect for mobile-first design
- Use **muted color palettes** to avoid overwhelming content
- Apply **blur effects** for softer, more elegant aesthetics
- Test backgrounds with **text overlay** to ensure readability
- Consider **subtle animations** by removing `py5.no_loop()` for interactive versions

## Resources

- [py5 Documentation](https://py5coding.org/)
- [Processing Reference](https://processing.org/reference/)
- [Perlin Noise Tutorial](https://www.khanacademy.org/computing/computer-programming/programming-natural-simulations/programming-noise/a/perlin-noise)
- [Generative Art Theory](https://tylerxhobbs.com/essays)

## License

MIT
