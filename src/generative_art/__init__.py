"""generative art package for algorithmic art generation.

provides flow field utilities, perlin noise animations, and tools for
generating natural-looking patterns.
"""

from generative_art.export import ResolutionConfig, export_multi_resolution
from generative_art.flow_field import (
    ClusteringConfig,
    FlowField,
    FlowFieldConfig,
    Obstacle,
    PointClusterer,
    create_clustered_points,
    create_flow_field_with_obstacles,
)

__all__ = [
    "ClusteringConfig",
    "FlowField",
    "FlowFieldConfig",
    "Obstacle",
    "PointClusterer",
    "ResolutionConfig",
    "create_clustered_points",
    "create_flow_field_with_obstacles",
    "export_multi_resolution",
]
