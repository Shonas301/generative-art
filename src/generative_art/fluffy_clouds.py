"""Procedural cloud generation using fractional Brownian motion.

This sketch demonstrates:
- fBm (fractional Brownian motion) with Perlin noise
- Multi-octave layering for organic cloud shapes
- Pink-to-blue gradient color mapping
- Domain warping for natural cloud distortion
- Soft post-processing for calming aesthetic
"""

from pathlib import Path

import click
import py5
from noise import pnoise2
from py5 import Sketch


class FluffyClouds(Sketch):
    """Generate soft, fluffy clouds using layered Perlin noise."""

    def __init__(
        self, width: int = 1920, height: int = 1080, output_path: str | None = None
    ) -> None:
        """Initialize the sketch parameters.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            output_path: If provided, save output to this path
        """
        super().__init__()
        self.canvas_width = width
        self.canvas_height = height
        self.output_path = output_path

        # fBm parameters
        self.octaves = 6
        self.persistence = 0.55  # how much each octave contributes
        self.lacunarity = 2.0  # frequency multiplier between octaves
        self.noise_scale = 0.002  # base scale for noise sampling

        # domain warping for organic distortion
        self.warp_strength = 40.0
        self.warp_scale = 0.001

        # cloud density thresholds
        self.cloud_threshold = 0.3  # values above this are clouds
        self.cloud_softness = 0.2  # gradient falloff range

    def settings(self) -> None:
        """Configure the sketch size and renderer."""
        self.size(self.canvas_width, self.canvas_height)

    def setup(self) -> None:
        """Set up the drawing environment."""
        # soft sky blue background
        self.background(173, 216, 230)
        self.no_loop()
        self.no_stroke()

    def draw(self) -> None:
        """Main drawing function."""
        # draw clouds using rectangles (safer than pixel manipulation in py5)
        self.no_stroke()

        # sample at lower resolution for performance, then upscale with blur
        sample_step = 2  # sample every 2nd pixel

        for y in range(0, self.canvas_height, sample_step):
            for x in range(0, self.canvas_width, sample_step):
                # calculate cloud density at this position
                cloud_value = self.fbm_noise(x, y)

                # map cloud value to color
                r, g, b, a = self.cloud_color(cloud_value, x, y)

                # only draw if there's some opacity
                if a > 5:
                    self.fill(r, g, b, a)
                    self.rect(x, y, sample_step, sample_step)

        # apply multiple blur passes for soft, dreamy look
        self.apply_filter(self.BLUR, 3)

        # save if output path provided
        if self.output_path:
            # use py5 module-level save (not self.save) for correct resolution handling
            py5.save(self.output_path)
            print(f"    Saved: {self.output_path}")
            self.exit_sketch()

    def fbm_noise(self, x: float, y: float) -> float:
        """Calculate fractional Brownian motion noise at position.

        Uses domain warping for organic cloud distortion.

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels

        Returns:
            Noise value in range [0, 1]
        """
        # domain warping - use noise to distort sampling positions
        warp_x = pnoise2(
            x * self.warp_scale,
            y * self.warp_scale,
            octaves=2,
        )
        warp_y = pnoise2(
            x * self.warp_scale + 100,
            y * self.warp_scale + 100,
            octaves=2,
        )

        # apply warp distortion
        warped_x = x + warp_x * self.warp_strength
        warped_y = y + warp_y * self.warp_strength

        # calculate fBm with multiple octaves
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0  # for normalization

        for _ in range(self.octaves):
            # sample noise at current frequency
            noise_val = pnoise2(
                warped_x * self.noise_scale * frequency,
                warped_y * self.noise_scale * frequency,
            )

            # accumulate weighted noise
            total += noise_val * amplitude
            max_value += amplitude

            # update for next octave
            amplitude *= self.persistence
            frequency *= self.lacunarity

        # normalize to [0, 1]
        normalized = (total / max_value + 1.0) / 2.0
        return normalized

    def cloud_color(
        self, cloud_value: float, x: float, y: float
    ) -> tuple[int, int, int, int]:
        """Map cloud density to color with pink-to-blue gradient.

        Args:
            cloud_value: Noise value from fbm_noise (0-1)
            x: X coordinate for gradient variation
            y: Y coordinate for gradient variation

        Returns:
            Tuple of (r, g, b, a) color values
        """
        # if below threshold, no cloud (transparent)
        if cloud_value < self.cloud_threshold:
            return (255, 255, 255, 0)

        # calculate cloud alpha with soft falloff
        alpha_range = cloud_value - self.cloud_threshold
        alpha = min(255, int((alpha_range / self.cloud_softness) * 255))

        # create vertical gradient from pink (top) to blue (bottom)
        gradient_pos = y / self.canvas_height

        # pink color (top): soft peachy pink
        pink_r, pink_g, pink_b = 255, 182, 193

        # blue color (bottom): soft periwinkle blue
        blue_r, blue_g, blue_b = 176, 196, 222

        # interpolate between pink and blue based on vertical position
        r = int(pink_r + (blue_r - pink_r) * gradient_pos)
        g = int(pink_g + (blue_g - pink_g) * gradient_pos)
        b = int(pink_b + (blue_b - pink_b) * gradient_pos)

        # add subtle brightness variation based on cloud density
        brightness = 0.9 + (cloud_value * 0.3)
        r = int(min(255, r * brightness))
        g = int(min(255, g * brightness))
        b = int(min(255, b * brightness))

        # reduce alpha slightly for softer look
        alpha = int(alpha * 0.85)

        return (r, g, b, alpha)


def parse_resolution(resolution_str: str) -> tuple[int, int]:
    """Parse resolution string to (width, height) tuple.

    Args:
        resolution_str: Resolution as shorthand (e.g., "1080p", "4k") or "WIDTHxHEIGHT"

    Returns:
        Tuple of (width, height) in pixels

    Raises:
        ValueError: If resolution string is invalid
    """
    # map of common shorthand names to resolutions
    shorthand_map = {
        "4k": (3840, 2160),
        "1440p": (2560, 1440),
        "1080p": (1920, 1080),
        "720p": (1280, 720),
        "1440p_portrait": (1440, 2560),
        "qhd_portrait": (1440, 2560),
    }

    # try shorthand first
    resolution_lower = resolution_str.lower()
    if resolution_lower in shorthand_map:
        return shorthand_map[resolution_lower]

    # try WIDTHxHEIGHT format
    if "x" in resolution_str:
        try:
            parts = resolution_str.split("x")
            if len(parts) == 2:
                width = int(parts[0])
                height = int(parts[1])
                if width > 0 and height > 0:
                    return (width, height)
        except ValueError:
            pass

    # if we get here, format is invalid
    valid_formats = ", ".join(shorthand_map.keys())
    msg = (
        f"invalid resolution: '{resolution_str}'. "
        f"use shorthand ({valid_formats}) or WIDTHxHEIGHT format (e.g., '1920x1080')"
    )
    raise ValueError(msg)


def render_all_resolutions(output_dir: str = "../../output") -> None:
    """Render sketch at all standard resolutions.

    Args:
        output_dir: Directory to save outputs
    """
    resolutions = {
        "4k": (3840, 2160),
        "1080p": (1920, 1080),
        "qhd_portrait": (1440, 2560),
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n🎨 Rendering fluffy clouds at multiple resolutions...")

    for res_name, (width, height) in resolutions.items():
        output_file = output_path / f"fluffy_clouds_{res_name}.png"
        print(f"  ├─ {res_name} ({width}x{height})...")

        sketch = FluffyClouds(width=width, height=height, output_path=str(output_file))
        sketch.run_sketch(block=True)

    print("✨ All renders complete!\n")


@click.command()
@click.option(
    "--render",
    is_flag=True,
    help="render static image instead of preview",
)
@click.option(
    "--resolution",
    default="1080p",
    help="resolution as shorthand (1080p, 4k, etc.) or WIDTHxHEIGHT (e.g., 1920x1080)",
)
@click.option(
    "--output",
    default="output/fluffy_clouds.png",
    help="output file path (only used with --render)",
)
def main(render: bool, resolution: str, output: str) -> None:
    """Run the sketch in different modes.

    preview mode (default): live window display
    render mode (--render): save static image to disk
    """
    # parse resolution
    try:
        resolution_tuple = parse_resolution(resolution)
    except ValueError as e:
        click.echo(f"error: {e}", err=True)
        raise click.Abort()

    width, height = resolution_tuple

    if render:
        # render mode - save to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        click.echo(f"🎨 rendering fluffy clouds...")
        click.echo(f"   resolution: {resolution} ({width}x{height})")
        click.echo(f"   output: {output_path.absolute()}")

        sketch = FluffyClouds(
            width=width, height=height, output_path=str(output_path)
        )
        sketch.run_sketch(block=True)

        click.echo("✨ render complete!")
    else:
        # preview mode - show in window
        click.echo("🎨 preview mode. close window to stop.")
        click.echo(f"   resolution: {resolution} ({width}x{height})")
        click.echo("   run with --render to save to file")
        click.echo("   use --help for all options")

        sketch = FluffyClouds(width=width, height=height)
        sketch.run_sketch()


if __name__ == "__main__":
    main()
