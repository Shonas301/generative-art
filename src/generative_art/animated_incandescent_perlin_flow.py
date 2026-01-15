"""Flow field visualization using Perlin noise.

This sketch demonstrates:
- Noise-based pattern generation
- Particle system with transforms
- Smooth color gradients
- Layered composition
"""

from pathlib import Path

import click
from noise import pnoise3
from py5 import Sketch


class AnimatedIncandesceeentPerlinFlow(Sketch):
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
        self.time_offset = 0.0  # time dimension for evolving noise field
        self.particles: list[list[float]] = []

    def settings(self) -> None:
        """Configure the sketch size and renderer."""
        self.size(self.canvas_width, self.canvas_height)

    def setup(self) -> None:
        """Set up the drawing environment."""
        self.background(8, 10, 20)
        # note: no no_loop() call - this enables animation

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
        # clear canvas each frame for animation
        self.background(8, 10, 20)

        # draw flow lines for each particle
        for i, particle in enumerate(self.particles):
            self.draw_flow_line(particle, i)

        # apply blur for smooth aesthetic
        self.apply_filter(self.BLUR, 1)

        # advance time for next frame
        self.time_offset += 0.5  # controls speed of field evolution

        # save frame if rendering animation
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
            # get noise value at current position with time dimension
            noise_val = pnoise3(
                x * self.noise_scale,
                y * self.noise_scale,
                self.time_offset * 0.01,  # time dimension - evolves the field
                octaves=3,
                persistence=0.5
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


def get_resolution_shorthand(width: int, height: int) -> str:
    """Convert resolution to shorthand notation.

    Args:
        width: Width in pixels
        height: Height in pixels

    Returns:
        Shorthand string like "1080p", "4k", "720p", etc.
    """
    common_resolutions = {
        (3840, 2160): "4k",
        (2560, 1440): "1440p",
        (1920, 1080): "1080p",
        (1280, 720): "720p",
        (1440, 2560): "1440p_portrait",
    }

    resolution = (width, height)
    if resolution in common_resolutions:
        return common_resolutions[resolution]
    else:
        return f"{width}x{height}"


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


def render_animation_sequential(
    output_dir: str = "./output",
    num_frames: int = 900,
    resolution: tuple[int, int] = (1920, 1080),  # default to 1080p for space savings
    seed: int | None = None,
) -> None:
    """Render animation frames sequentially (macOS-compatible).

    note: parallel rendering with py5 on macOS is not supported due to JVM/GUI limitations.
    on macOS, P2D/P3D renderers cannot run headless and multiprocessing causes JVM crashes.
    this sequential approach is reliable and works on all platforms.

    Args:
        output_dir: Directory to save frame sequence
        num_frames: Number of frames to render (900 = 30 sec at 30fps)
        resolution: (width, height) tuple
        seed: Random seed for deterministic output (auto-generated if not provided)
    """
    import random
    import time

    # generate seed if not provided
    if seed is None:
        seed = random.randint(0, 999999)

    width, height = resolution
    res_shorthand = get_resolution_shorthand(width, height)

    output_path = Path(output_dir) / "frames"
    output_path.mkdir(parents=True, exist_ok=True)

    seed_str = f"s{seed}"
    click.echo(f"\n🎬 rendering {num_frames} frames at {width}x{height} ({res_shorthand})")
    click.echo(f"   seed: {seed} (use --seed {seed} to reproduce)")
    click.echo(f"\n   📁 OUTPUT DIRECTORY: {output_path.absolute()}")
    click.echo(f"   files will be saved as: {res_shorthand}_{seed_str}_frame_NNNN.png\n")
    click.echo(f"   ⏱️  estimated time: ~{num_frames * 2 / 60:.0f}-{num_frames * 4 / 60:.0f} minutes")
    click.echo(f"   (actual time varies based on resolution and system performance)\n")

    class SequentialRenderer(AnimatedIncandesceeentPerlinFlow):
        """Sequential renderer that saves each frame."""

        def __init__(self) -> None:
            """Initialize sequential renderer."""
            super().__init__(width=width, height=height)
            self.frame_num = 0
            self.total_frames = num_frames
            self.start_time = time.time()

        def setup(self) -> None:
            """Set up the drawing environment with seed."""
            self.random_seed(seed)

            # call parent setup
            super().setup()

        def draw(self) -> None:
            """Draw and save frame."""
            # clear canvas each frame for animation
            self.background(8, 10, 20)

            # draw flow lines for each particle
            for i, particle in enumerate(self.particles):
                self.draw_flow_line(particle, i)

            # apply blur for smooth aesthetic
            self.apply_filter(self.BLUR, 1)

            # save frame with resolution, seed, and zero-padded numbering
            # format: {resolution}_{seed}_frame_{number}.png
            # example: 1080p_s42_frame_0000.png
            frame_file = output_path / f"{res_shorthand}_{seed_str}_frame_{self.frame_num:04d}.png"
            self.save(str(frame_file))

            # progress reporting
            if self.frame_num % 10 == 0 or self.frame_num == 0:
                progress = (self.frame_num + 1) / self.total_frames * 100
                elapsed = time.time() - self.start_time
                frames_per_sec = (self.frame_num + 1) / elapsed if elapsed > 0 else 0
                remaining_frames = self.total_frames - (self.frame_num + 1)
                eta_seconds = remaining_frames / frames_per_sec if frames_per_sec > 0 else 0
                eta_mins = int(eta_seconds / 60)
                eta_secs = int(eta_seconds % 60)

                click.echo(
                    f"   frame {self.frame_num:04d}/{self.total_frames} "
                    f"({progress:5.1f}%) - "
                    f"{frames_per_sec:.2f} fps - "
                    f"eta: {eta_mins:02d}:{eta_secs:02d}"
                )

            self.frame_num += 1
            self.time_offset += 0.5

            # stop when complete
            if self.frame_num >= self.total_frames:
                elapsed = time.time() - self.start_time
                click.echo(f"\n✨ rendering complete in {elapsed / 60:.1f} minutes!")
                click.echo(f"\n📹 compile animation with ffmpeg:")
                click.echo(f"   cd {output_path.absolute()}")
                click.echo(
                    f"   ffmpeg -framerate 30 -i '{res_shorthand}_{seed_str}_frame_%04d.png' "
                    f"-c:v libx264 -pix_fmt yuv420p ../{res_shorthand}_{seed_str}_animation.mp4\n"
                )
                self.exit_sketch()

    sketch = SequentialRenderer()
    sketch.run_sketch(block=True)


@click.command()
@click.option(
    "--render-animation",
    is_flag=True,
    help="render animation frames instead of live preview",
)
@click.option(
    "--resolution",
    default="1080p",
    help="resolution as shorthand (1080p, 4k, etc.) or WIDTHxHEIGHT (e.g., 1920x1080)",
)
@click.option(
    "--frames",
    default=900,
    type=int,
    help="number of frames to render (default: 900 = 30 sec at 30fps)",
)
@click.option(
    "--seed",
    default=None,
    type=int,
    help="random seed for deterministic output (auto-generated if not provided)",
)
@click.option(
    "--output-dir",
    default="./output",
    help="directory to save rendered frames (default: ./output)",
)
def main(
    render_animation: bool,
    resolution: str,
    frames: int,
    seed: int | None,
    output_dir: str,
) -> None:
    """Run the sketch in different modes.

    preview mode (default): live animation in window
    render mode (--render-animation): save animation frames to disk
    """
    if render_animation:
        # parse resolution
        try:
            resolution_tuple = parse_resolution(resolution)
        except ValueError as e:
            click.echo(f"error: {e}", err=True)
            raise click.Abort()

        # sequential rendering - parallel not supported on macOS due to JVM/GUI limitations
        render_animation_sequential(
            output_dir=output_dir,
            num_frames=frames,
            resolution=resolution_tuple,
            seed=seed,
        )
    else:
        # preview mode - live animation in window
        try:
            resolution_tuple = parse_resolution(resolution)
        except ValueError as e:
            click.echo(f"error: {e}", err=True)
            raise click.Abort()

        width, height = resolution_tuple
        click.echo("🎬 live animation preview. close window to stop.")
        click.echo(f"   resolution: {resolution} ({width}x{height})")
        click.echo("   run with --render-animation to save frames")
        click.echo("   use --help for all options")

        sketch = AnimatedIncandesceeentPerlinFlow(width=width, height=height)
        sketch.run_sketch()


if __name__ == "__main__":
    main()
