"""Maya grass generation plugin using flow fields.

This module provides tools for generating natural-looking animated grass in
Autodesk Maya. it integrates with the generative_art.flow_field module to
create wind-responsive grass that flows around obstacles.

usage:
    # in maya's script editor (python):
    from maya_grass import GrassGenerator

    # create generator from selected terrain mesh
    grass = GrassGenerator.from_selection()

    # detect obstacles from bump map threshold
    grass.detect_obstacles_from_bump(threshold=0.5)

    # generate grass points clustered around obstacles
    grass.generate_points(count=10000)

    # create MASH network for instancing
    grass.create_mash_network(grass_geometry="grassBlade")

features:
    - bump/displacement map obstacle detection
    - wind flow field with obstacle avoidance
    - point clustering around obstacles
    - MASH integration for efficient instancing
    - animation support via expression-driven flow
    - export to JSON for external tools
"""

from maya_grass.generator import GrassGenerator
from maya_grass.terrain import TerrainAnalyzer
from maya_grass.wind import WindField

__all__ = [
    "GrassGenerator",
    "TerrainAnalyzer",
    "WindField",
]
