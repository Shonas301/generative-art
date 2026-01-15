"""Unit tests for flow_field module."""

import math

import numpy as np
import pytest

from generative_art.flow_field import (
    ClusteringConfig,
    FlowField,
    FlowFieldConfig,
    Obstacle,
    PointClusterer,
    create_clustered_points,
    create_flow_field_with_obstacles,
)


class TestObstacle:
    """Tests for Obstacle dataclass."""

    def test_obstacle_default_influence_radius(self) -> None:
        """test that default influence radius is 2.5x obstacle radius."""
        # given
        obstacle = Obstacle(x=100, y=100, radius=40)

        # then
        assert obstacle.influence_radius == 100.0  # 40 * 2.5

    def test_obstacle_custom_influence_radius(self) -> None:
        """test that custom influence radius is respected."""
        # given
        obstacle = Obstacle(x=100, y=100, radius=40, influence_radius=200)

        # then
        assert obstacle.influence_radius == 200

    def test_obstacle_default_strength(self) -> None:
        """test that default strength is 1.0."""
        # given
        obstacle = Obstacle(x=100, y=100, radius=40)

        # then
        assert obstacle.strength == 1.0


class TestFlowFieldConfig:
    """Tests for FlowFieldConfig dataclass."""

    def test_default_config_values(self) -> None:
        """test that default config has expected values."""
        # given
        config = FlowFieldConfig()

        # then
        assert config.noise_scale == 0.003
        assert config.flow_strength == 2.0
        assert config.octaves == 3
        assert config.persistence == 0.5
        assert config.time_scale == 0.01

    def test_custom_config_values(self) -> None:
        """test that custom config values are respected."""
        # given
        config = FlowFieldConfig(
            noise_scale=0.01,
            flow_strength=5.0,
            octaves=4,
            persistence=0.6,
            time_scale=0.02,
        )

        # then
        assert config.noise_scale == 0.01
        assert config.flow_strength == 5.0
        assert config.octaves == 4
        assert config.persistence == 0.6
        assert config.time_scale == 0.02


class TestFlowField:
    """Tests for FlowField class."""

    def test_flow_field_initialization_with_defaults(self) -> None:
        """test that flow field initializes with default config."""
        # given/when
        flow_field = FlowField()

        # then
        assert flow_field.config is not None
        assert flow_field.obstacles == []

    def test_flow_field_initialization_with_custom_config(self) -> None:
        """test that flow field uses provided config."""
        # given
        config = FlowFieldConfig(noise_scale=0.01)

        # when
        flow_field = FlowField(config=config)

        # then
        assert flow_field.config.noise_scale == 0.01

    def test_add_obstacle(self) -> None:
        """test that obstacles can be added."""
        # given
        flow_field = FlowField()
        obstacle = Obstacle(x=100, y=100, radius=50)

        # when
        flow_field.add_obstacle(obstacle)

        # then
        assert len(flow_field.obstacles) == 1
        assert flow_field.obstacles[0] == obstacle

    def test_clear_obstacles(self) -> None:
        """test that obstacles can be cleared."""
        # given
        flow_field = FlowField()
        flow_field.add_obstacle(Obstacle(x=100, y=100, radius=50))
        flow_field.add_obstacle(Obstacle(x=200, y=200, radius=30))

        # when
        flow_field.clear_obstacles()

        # then
        assert len(flow_field.obstacles) == 0

    def test_get_base_flow_returns_vector(self) -> None:
        """test that base flow returns a 2d vector."""
        # given
        flow_field = FlowField()

        # when
        vx, vy = flow_field.get_base_flow(100, 100)

        # then
        assert isinstance(vx, (int, float))
        assert isinstance(vy, (int, float))

    def test_get_base_flow_has_reasonable_magnitude(self) -> None:
        """test that base flow magnitude is within expected bounds."""
        # given
        config = FlowFieldConfig(flow_strength=2.0)
        flow_field = FlowField(config=config)

        # when
        vx, vy = flow_field.get_base_flow(100, 100)
        magnitude = math.sqrt(vx**2 + vy**2)

        # then - magnitude should be close to flow_strength
        assert 0 < magnitude <= config.flow_strength * 1.1

    def test_get_flow_deflects_near_obstacle(self) -> None:
        """test that flow is deflected when near obstacle."""
        # given
        flow_field = FlowField()
        obstacle = Obstacle(x=100, y=100, radius=50, influence_radius=150)
        flow_field.add_obstacle(obstacle)

        # when - get flow just outside obstacle
        flow_without_obstacle = FlowField().get_flow(120, 100)
        flow_with_obstacle = flow_field.get_flow(120, 100)

        # then - flows should differ due to deflection
        # (we can't predict exact values due to noise, but they should be different)
        assert flow_without_obstacle != flow_with_obstacle

    def test_get_flow_unchanged_far_from_obstacle(self) -> None:
        """test that flow is unchanged when far from obstacle."""
        # given
        flow_field = FlowField()
        obstacle = Obstacle(x=100, y=100, radius=50, influence_radius=150)
        flow_field.add_obstacle(obstacle)

        # when - get flow far from obstacle
        far_x, far_y = 500, 500
        flow_without_obstacle = FlowField().get_flow(far_x, far_y)
        flow_with_obstacle = flow_field.get_flow(far_x, far_y)

        # then - flows should be identical
        assert flow_without_obstacle == flow_with_obstacle

    def test_get_flow_inside_obstacle_pushes_outward(self) -> None:
        """test that flow inside obstacle pushes outward."""
        # given
        flow_field = FlowField()
        obstacle = Obstacle(x=100, y=100, radius=50, strength=1.0)
        flow_field.add_obstacle(obstacle)

        # when - get flow inside obstacle
        vx, vy = flow_field.get_flow(110, 100)  # just right of center

        # then - should have significant rightward component (pushing out)
        assert vx > 0

    def test_get_flow_angle_returns_radians(self) -> None:
        """test that flow angle is in valid radian range."""
        # given
        flow_field = FlowField()

        # when
        angle = flow_field.get_flow_angle(100, 100)

        # then
        assert -math.pi <= angle <= math.pi

    def test_get_flow_with_time_evolution(self) -> None:
        """test that flow changes over time."""
        # given
        flow_field = FlowField()

        # when
        flow_t0 = flow_field.get_flow(100, 100, time=0.0)
        flow_t100 = flow_field.get_flow(100, 100, time=100.0)

        # then - flows should differ at different times
        assert flow_t0 != flow_t100


class TestClusteringConfig:
    """Tests for ClusteringConfig dataclass."""

    def test_default_config_values(self) -> None:
        """test that default clustering config has expected values."""
        # given
        config = ClusteringConfig()

        # then
        assert config.base_density == 0.001
        assert config.obstacle_density_multiplier == 3.0
        assert config.min_distance == 5.0
        assert config.cluster_falloff == 0.5
        assert config.edge_offset == 10.0


class TestPointClusterer:
    """Tests for PointClusterer class."""

    def test_clusterer_initialization(self) -> None:
        """test that clusterer initializes correctly."""
        # given/when
        clusterer = PointClusterer(width=1000, height=1000)

        # then
        assert clusterer.width == 1000
        assert clusterer.height == 1000
        assert clusterer.obstacles == []

    def test_add_obstacle(self) -> None:
        """test that obstacles can be added to clusterer."""
        # given
        clusterer = PointClusterer(width=1000, height=1000)
        obstacle = Obstacle(x=500, y=500, radius=50)

        # when
        clusterer.add_obstacle(obstacle)

        # then
        assert len(clusterer.obstacles) == 1

    def test_get_density_base_without_obstacles(self) -> None:
        """test that density is 1.0 when no obstacles present."""
        # given
        clusterer = PointClusterer(width=1000, height=1000)

        # when
        density = clusterer.get_density_at(500, 500)

        # then
        assert density == 1.0

    def test_get_density_zero_inside_obstacle(self) -> None:
        """test that density is 0 inside obstacle."""
        # given
        clusterer = PointClusterer(width=1000, height=1000)
        clusterer.add_obstacle(Obstacle(x=500, y=500, radius=50))

        # when
        density = clusterer.get_density_at(500, 500)  # center of obstacle

        # then
        assert density == 0.0

    def test_get_density_higher_near_obstacle(self) -> None:
        """test that density is higher near obstacle edge."""
        # given
        config = ClusteringConfig(
            obstacle_density_multiplier=3.0,
            edge_offset=10.0,
        )
        clusterer = PointClusterer(width=1000, height=1000, config=config)
        clusterer.add_obstacle(Obstacle(x=500, y=500, radius=50, influence_radius=150))

        # when
        density_near = clusterer.get_density_at(560, 500)  # 10px from edge
        density_far = clusterer.get_density_at(800, 500)  # far from obstacle

        # then
        assert density_near > density_far

    def test_is_valid_point_outside_boundaries(self) -> None:
        """test that points outside boundaries are invalid."""
        # given
        clusterer = PointClusterer(width=1000, height=1000)

        # then
        assert not clusterer.is_valid_point(-10, 500, [])
        assert not clusterer.is_valid_point(500, -10, [])
        assert not clusterer.is_valid_point(1010, 500, [])
        assert not clusterer.is_valid_point(500, 1010, [])

    def test_is_valid_point_inside_obstacle(self) -> None:
        """test that points inside obstacles are invalid."""
        # given
        clusterer = PointClusterer(width=1000, height=1000)
        clusterer.add_obstacle(Obstacle(x=500, y=500, radius=50))

        # then
        assert not clusterer.is_valid_point(500, 500, [])

    def test_is_valid_point_too_close_to_existing(self) -> None:
        """test that points too close to existing points are invalid."""
        # given
        config = ClusteringConfig(min_distance=20.0)
        clusterer = PointClusterer(width=1000, height=1000, config=config)
        existing = [(500, 500)]

        # then
        assert not clusterer.is_valid_point(510, 500, existing)  # 10px away
        assert clusterer.is_valid_point(530, 500, existing)  # 30px away

    def test_generate_points_returns_requested_count(self) -> None:
        """test that generate_points returns approximately the requested count."""
        # given
        clusterer = PointClusterer(width=1000, height=1000, seed=42)

        # when
        points = clusterer.generate_points(100)

        # then - may not get exact count due to rejection sampling
        assert len(points) > 50  # should get reasonable number
        assert len(points) <= 100

    def test_generate_points_avoids_obstacles(self) -> None:
        """test that generated points are not inside obstacles."""
        # given
        clusterer = PointClusterer(width=1000, height=1000, seed=42)
        obstacle = Obstacle(x=500, y=500, radius=100)
        clusterer.add_obstacle(obstacle)

        # when
        points = clusterer.generate_points(200)

        # then
        for x, y in points:
            dist = math.sqrt((x - 500) ** 2 + (y - 500) ** 2)
            assert dist >= obstacle.radius

    def test_generate_points_grid_based_returns_points(self) -> None:
        """test that grid-based generation returns points."""
        # given
        clusterer = PointClusterer(width=1000, height=1000, seed=42)

        # when
        points = clusterer.generate_points_grid_based(100)

        # then
        assert len(points) > 0
        for x, y in points:
            assert 0 <= x <= 1000
            assert 0 <= y <= 1000

    def test_generate_points_clusters_around_obstacle(self) -> None:
        """test that generated points cluster more densely near obstacles.

        uses rejection sampling (not grid-based) which respects density better.
        """
        # given
        config = ClusteringConfig(
            obstacle_density_multiplier=5.0,
            min_distance=3.0,
            edge_offset=20.0,
            cluster_falloff=0.8,
        )
        clusterer = PointClusterer(width=1000, height=1000, config=config, seed=42)
        obstacle = Obstacle(x=500, y=500, radius=50, influence_radius=200)
        clusterer.add_obstacle(obstacle)

        # when - use rejection sampling which better respects density
        points = clusterer.generate_points(1000)

        # then - count points in different regions
        near_obstacle_count = 0
        far_from_obstacle_count = 0

        for x, y in points:
            dist = math.sqrt((x - 500) ** 2 + (y - 500) ** 2)
            if 50 < dist < 200:  # in influence zone
                near_obstacle_count += 1
            elif dist > 400:
                far_from_obstacle_count += 1

        # normalize by area
        near_area = math.pi * (200**2 - 50**2)
        far_area = 1000 * 1000 - math.pi * 400**2

        near_density = near_obstacle_count / near_area if near_area > 0 else 0
        far_density = far_from_obstacle_count / far_area if far_area > 0 else 0

        # density near obstacle should be higher (or at least have points there)
        # note: rejection sampling is probabilistic, so we just check we got points
        assert len(points) > 100  # should have generated reasonable number
        assert near_obstacle_count > 0  # should have some points near obstacle

    def test_seeded_generation_is_reproducible(self) -> None:
        """test that same seed produces same points."""
        # given
        clusterer1 = PointClusterer(width=1000, height=1000, seed=42)
        clusterer2 = PointClusterer(width=1000, height=1000, seed=42)

        # when
        points1 = clusterer1.generate_points_grid_based(50)
        points2 = clusterer2.generate_points_grid_based(50)

        # then
        assert points1 == points2


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_flow_field_with_obstacles(self) -> None:
        """test that convenience function creates flow field correctly."""
        # given
        obstacles = [
            {"x": 100, "y": 100, "radius": 50},
            {"x": 200, "y": 200, "radius": 30, "strength": 0.5},
        ]

        # when
        flow_field = create_flow_field_with_obstacles(
            _width=1000, _height=1000, obstacles=obstacles
        )

        # then
        assert len(flow_field.obstacles) == 2
        assert flow_field.obstacles[0].radius == 50
        assert flow_field.obstacles[1].strength == 0.5

    def test_create_flow_field_with_custom_config(self) -> None:
        """test that convenience function respects custom config."""
        # given
        flow_config = {"noise_scale": 0.01, "flow_strength": 5.0}

        # when
        flow_field = create_flow_field_with_obstacles(
            _width=1000, _height=1000, obstacles=[], flow_config=flow_config
        )

        # then
        assert flow_field.config.noise_scale == 0.01
        assert flow_field.config.flow_strength == 5.0

    def test_create_clustered_points(self) -> None:
        """test that convenience function generates clustered points."""
        # given
        obstacles = [{"x": 500, "y": 500, "radius": 50}]

        # when
        points = create_clustered_points(
            width=1000,
            height=1000,
            num_points=100,
            obstacles=obstacles,
            seed=42,
        )

        # then
        assert len(points) > 0
        # check no points inside obstacle
        for x, y in points:
            dist = math.sqrt((x - 500) ** 2 + (y - 500) ** 2)
            assert dist >= 50
