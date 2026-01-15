"""Export utilities for multi-resolution rendering."""

from pathlib import Path
from typing import Any

import py5


class ResolutionConfig:
    """Configuration for different output resolutions."""

    UHD_4K = (3840, 2160)
    FULL_HD = (1920, 1080)
    QHD_PORTRAIT = (1440, 2560)

    ALL_RESOLUTIONS = {
        "4k": UHD_4K,
        "1080p": FULL_HD,
        "qhd_portrait": QHD_PORTRAIT,
    }


def export_multi_resolution(
    sketch_class: type,
    sketch_name: str,
    output_dir: str = "outputs",
    resolutions: dict[str, tuple[int, int]] | None = None,
) -> None:
    """Export a sketch at multiple resolutions.

    Args:
        sketch_class: The sketch class to instantiate and render
        sketch_name: Base name for output files (e.g., "rotating_fractals")
        output_dir: Directory to save outputs (default: "outputs")
        resolutions: Dict of resolution names to (width, height) tuples.
                    If None, uses all default resolutions.
    """
    if resolutions is None:
        resolutions = ResolutionConfig.ALL_RESOLUTIONS

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n🎨 Rendering {sketch_name}...")

    for res_name, (width, height) in resolutions.items():
        print(f"  ├─ {res_name} ({width}x{height})...", end=" ", flush=True)

        # Create sketch instance with specified resolution
        sketch = sketch_class()
        sketch.width = width
        sketch.height = height

        # Run sketch and save
        output_file = output_path / f"{sketch_name}_{res_name}.png"

        # Add save call to the draw method
        original_draw = sketch.draw

        def draw_and_save() -> None:
            """Wrapper to call original draw and save."""
            original_draw()
            py5.save(str(output_file))

        sketch.draw = draw_and_save

        # Run the sketch
        py5.run_sketch(py5_object=sketch)

        print("✓")

    print(f"\n✨ All renders complete! Saved to: {output_path.absolute()}\n")


def create_output_structure(base_dir: str = "outputs") -> dict[str, Path]:
    """Create organized output directory structure.

    Args:
        base_dir: Base output directory name

    Returns:
        Dictionary mapping resolution names to their directory paths
    """
    base_path = Path(base_dir)
    paths = {}

    for res_name in ResolutionConfig.ALL_RESOLUTIONS:
        res_path = base_path / res_name
        res_path.mkdir(parents=True, exist_ok=True)
        paths[res_name] = res_path

    return paths
