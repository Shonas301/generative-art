"""CLI entry point for generative_art package.

allows running sketches via: python -m generative_art <command>
"""

import click

from generative_art.animated_incandescent_perlin_flow import (
    main as animated_perlin_main,
)
from generative_art.incandescent_perlin_flow import main as perlin_main


@click.group()
def cli() -> None:
    """generative art sketches using py5.

    run sketches in preview mode or render to files at various resolutions.
    """
    pass


# add subcommands with descriptive names
cli.add_command(animated_perlin_main, name="animated-perlin")
cli.add_command(perlin_main, name="perlin")


if __name__ == "__main__":
    cli()
