"""Flow field visualization using Perlin noise.

This sketch demonstrates:
- Noise-based pattern generation
- Particle system with transforms
- Smooth color gradients
- Layered composition
"""

from pathlib import Path

import click
from noise import pnoise2
from py5 import Sketch


class IncandesceeentPerlinFlow(Sketch):
    """Generate flowing patterns based on Perlin noise fields."""

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
        self.num_particles = 3000
        self.noise_scale = 0.003
        self.flow_strength = 2.0
        self.particles: list[list[float]] = []

    def settings(self) -> None:
        """Configure the sketch size and renderer."""
        self.size(self.canvas_width, self.canvas_height)

    def setup(self) -> None:
        """Set up the drawing environment."""
        self.background(8, 10, 20)
        self.no_loop()

        # Calculate center
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2

        # Initialize particles at random positions (50% of total)
        random_count = int(self.num_particles * 0.5)
        for _ in range(random_count):
            x = self.random(self.canvas_width)
            y = self.random(self.canvas_height)
            self.particles.append([x, y])

        # Add particles in concentric rings around center (20% of total)
        # This ensures particles flow THROUGH the center area
        ring_count = int(self.num_particles * 0.2)
        num_rings = 5
        particles_per_ring = ring_count // num_rings

        for ring in range(num_rings):
            # Rings at different radii from very close to medium distance
            ring_radius = (ring + 1) * 80  # 80, 160, 240, 320, 400 pixels
            for _ in range(particles_per_ring):
                angle = self.random(self.TWO_PI)
                # Add some variation to the radius
                radius = ring_radius + self.random(-30, 30)
                x = center_x + self.cos(angle) * radius
                y = center_y + self.sin(angle) * radius
                self.particles.append([x, y])

        # Add MANY particles right AT the center (30% of total)
        # These will immediately start flowing outward/around
        exact_center_count = int(self.num_particles * 0.3)
        for _ in range(exact_center_count):
            # Very tight cluster at exact center
            angle = self.random(self.TWO_PI)
            radius = self.random(5)  # Within 5 pixels of dead center
            x = center_x + self.cos(angle) * radius
            y = center_y + self.sin(angle) * radius
            self.particles.append([x, y])

    def draw(self) -> None:
        """Main drawing function."""
        # Draw flow lines for each particle
        for i, particle in enumerate(self.particles):
            self.draw_flow_line(particle, i)

        # Apply blur for smooth aesthetic
        self.apply_filter(self.BLUR, 1)

        # Save if output path provided
        if self.output_path:
            self.save(self.output_path)
            print(f"    Saved: {self.output_path}")
            self.exit_sketch()

    def draw_flow_line(self, start_pos: list[float], particle_id: int) -> None:
        """Draw a flowing line following the noise field.

        Args:
            start_pos: Starting [x, y] position
            particle_id: Unique particle identifier for color variation
        """
        x, y = start_pos
        steps = 250  # Increased so particles travel further

        # Color based on particle position and ID
        hue = (particle_id * 0.5 + x * 0.1) % 360
        r = int((self.sin(hue * 0.02) + 1) * 100 + 80)
        g = int((self.cos(hue * 0.03 + 2) + 1) * 90 + 100)
        b = int((self.sin(hue * 0.025 + 4) + 1) * 100 + 120)

        self.stroke_weight(1.5)
        self.no_fill()

        # Draw line using individual line segments with changing colors
        prev_x, prev_y = x, y

        for step in range(steps):
            # Get noise value at current position
            noise_val = pnoise2(
                x * self.noise_scale, y * self.noise_scale, octaves=3, persistence=0.5
            )

            # Convert noise to angle
            angle = noise_val * self.TWO_PI * 2

            # Calculate velocity from angle
            vx = self.cos(angle) * self.flow_strength
            vy = self.sin(angle) * self.flow_strength

            # Update position
            x += vx
            y += vy

            # Boundary check - stop if off canvas
            if x < 0 or x > self.canvas_width or y < 0 or y > self.canvas_height:
                break

            # Fade alpha over the line
            alpha = 255 * (1 - step / steps) * 0.4

            # Update color slightly as we move
            r_shift = int(r + self.sin(step * 0.1) * 20)
            g_shift = int(g + self.cos(step * 0.1) * 20)
            b_shift = int(b + self.sin(step * 0.15) * 20)

            self.stroke(r_shift, g_shift, b_shift, alpha)

            # Draw line segment from previous position to current
            self.line(prev_x, prev_y, x, y)

            # Update previous position
            prev_x, prev_y = x, y


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

    print("\n🎨 Rendering incandescent perlin flow at multiple resolutions...")

    for res_name, (width, height) in resolutions.items():
        output_file = output_path / f"incandescent_perlin_flow_{res_name}.png"
        print(f"  ├─ {res_name} ({width}x{height})...")

        sketch = IncandesceeentPerlinFlow(width=width, height=height, output_path=str(output_file))
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
    default="output/incandescent_perlin_flow.png",
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

        click.echo(f"🎨 rendering incandescent perlin flow...")
        click.echo(f"   resolution: {resolution} ({width}x{height})")
        click.echo(f"   output: {output_path.absolute()}")

        sketch = IncandesceeentPerlinFlow(
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

        sketch = IncandesceeentPerlinFlow(width=width, height=height)
        sketch.run_sketch()


if __name__ == "__main__":
    main()
