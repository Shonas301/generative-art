"""Unit tests for noise_utils module."""

import pytest

from generative_art.noise_utils import fbm_noise1, fbm_noise2, fbm_noise3, init_noise


class TestInitNoise:
    """tests for init_noise function."""

    def test_init_noise_with_seed_is_deterministic(self) -> None:
        """test that same seed produces same noise values."""
        # given
        seed = 42

        # when
        init_noise(seed)
        first_value = fbm_noise2(0.5, 0.5)
        init_noise(seed)
        second_value = fbm_noise2(0.5, 0.5)

        # then
        assert first_value == second_value

    def test_init_noise_without_seed_runs_without_error(self) -> None:
        """test that init_noise with None seed does not raise."""
        # given
        seed = None

        # when / then
        init_noise(seed)  # should not raise

    def test_init_noise_different_seeds_produce_different_results(self) -> None:
        """test that different seeds produce different noise values."""
        # given
        seed_a = 42
        seed_b = 123

        # when
        init_noise(seed_a)
        value_a = fbm_noise2(0.5, 0.5)
        init_noise(seed_b)
        value_b = fbm_noise2(0.5, 0.5)

        # then
        assert value_a != value_b


class TestFbmNoise2:
    """tests for fbm_noise2 function."""

    def test_fbm_noise2_returns_float(self) -> None:
        """test that fbm_noise2 returns a float."""
        # given
        x, y = 0.5, 0.5

        # when
        result = fbm_noise2(x, y)

        # then
        assert isinstance(result, float)

    def test_fbm_noise2_output_in_range(self) -> None:
        """test that output is always in [-1.0, 1.0] range."""
        # given
        coords = [(0, 0), (1.5, 2.3), (-0.5, 100.0), (999.0, -888.0)]

        # when / then
        for x, y in coords:
            result = fbm_noise2(x, y)
            assert -1.0 <= result <= 1.0, f"out of range at ({x}, {y}): {result}"

    def test_fbm_noise2_defaults_work(self) -> None:
        """test that fbm_noise2 works with default parameters."""
        # given
        x, y = 0.5, 0.5

        # when
        result = fbm_noise2(x, y)  # no optional params

        # then
        assert isinstance(result, float)

    def test_fbm_noise2_octaves_affect_output(self) -> None:
        """test that different octave counts produce different outputs."""
        # given
        init_noise(42)
        x, y = 0.5, 0.5

        # when
        value_1_octave = fbm_noise2(x, y, octaves=1)
        value_4_octaves = fbm_noise2(x, y, octaves=4)

        # then
        assert value_1_octave != value_4_octaves

    def test_fbm_noise2_persistence_affects_output(self) -> None:
        """test that different persistence values produce different outputs."""
        # given
        init_noise(42)
        x, y = 0.5, 0.5

        # when
        value_low_persistence = fbm_noise2(x, y, octaves=3, persistence=0.3)
        value_high_persistence = fbm_noise2(x, y, octaves=3, persistence=0.7)

        # then
        assert value_low_persistence != value_high_persistence

    def test_fbm_noise2_lacunarity_affects_output(self) -> None:
        """test that different lacunarity values produce different outputs."""
        # given
        init_noise(42)
        x, y = 0.5, 0.5

        # when
        value_low_lacunarity = fbm_noise2(x, y, octaves=3, lacunarity=2.0)
        value_high_lacunarity = fbm_noise2(x, y, octaves=3, lacunarity=3.0)

        # then
        assert value_low_lacunarity != value_high_lacunarity

    def test_fbm_noise2_continuous(self) -> None:
        """test that nearby inputs produce nearby outputs (continuity)."""
        # given
        init_noise(42)
        x, y = 0.5, 0.5
        delta = 0.001

        # when
        value_base = fbm_noise2(x, y)
        value_nearby = fbm_noise2(x + delta, y)

        # then
        difference = abs(value_base - value_nearby)
        assert difference < 0.1, f"discontinuity: {difference}"

    def test_fbm_noise2_output_normalized_with_many_octaves(self) -> None:
        """test that output is normalized even with many octaves."""
        # given
        init_noise(42)
        coords = [(0, 0), (1.5, 2.3), (-0.5, 100.0), (999.0, -888.0)]
        octaves = 8

        # when / then
        for x, y in coords:
            result = fbm_noise2(x, y, octaves=octaves)
            assert -1.0 <= result <= 1.0, f"out of range at ({x}, {y}): {result}"


class TestFbmNoise3:
    """tests for fbm_noise3 function."""

    def test_fbm_noise3_returns_float(self) -> None:
        """test that fbm_noise3 returns a float."""
        # given
        x, y, z = 0.5, 0.5, 0.0

        # when
        result = fbm_noise3(x, y, z)

        # then
        assert isinstance(result, float)

    def test_fbm_noise3_output_in_range(self) -> None:
        """test that output is always in [-1.0, 1.0] range."""
        # given
        coords = [
            (0, 0, 0),
            (1.5, 2.3, 0.5),
            (-0.5, 100.0, 10.0),
            (999.0, -888.0, 50.0),
        ]

        # when / then
        for x, y, z in coords:
            result = fbm_noise3(x, y, z)
            assert -1.0 <= result <= 1.0, f"out of range at ({x}, {y}, {z}): {result}"

    def test_fbm_noise3_z_for_animation(self) -> None:
        """test that z parameter produces smooth variation (animation use case)."""
        # given
        init_noise(42)
        x, y = 0.5, 0.5
        z_values = [0.0, 0.1, 0.2, 1.0]

        # when
        results = [fbm_noise3(x, y, z) for z in z_values]

        # then
        # all values should be different (z affects output)
        assert len(set(results)) == len(results), "z values should produce different outputs"

        # adjacent z values should be reasonably close (smooth animation)
        for i in range(len(results) - 1):
            diff = abs(results[i] - results[i + 1])
            assert diff < 1.0, f"z transition too abrupt: {diff}"

    def test_fbm_noise3_output_normalized_with_many_octaves(self) -> None:
        """test that output is normalized even with many octaves."""
        # given
        init_noise(42)
        coords = [
            (0, 0, 0),
            (1.5, 2.3, 0.5),
            (-0.5, 100.0, 10.0),
            (999.0, -888.0, 50.0),
        ]
        octaves = 8

        # when / then
        for x, y, z in coords:
            result = fbm_noise3(x, y, z, octaves=octaves)
            assert -1.0 <= result <= 1.0, f"out of range at ({x}, {y}, {z}): {result}"


class TestFbmNoise1:
    """tests for fbm_noise1 function."""

    def test_fbm_noise1_returns_float(self) -> None:
        """test that fbm_noise1 returns a float."""
        # given
        x = 0.5

        # when
        result = fbm_noise1(x)

        # then
        assert isinstance(result, float)

    def test_fbm_noise1_output_in_range(self) -> None:
        """test that output is always in [-1.0, 1.0] range."""
        # given
        x_values = [0, 0.5, 1.5, -0.5, 100.0, 999.0]

        # when / then
        for x in x_values:
            result = fbm_noise1(x)
            assert -1.0 <= result <= 1.0, f"out of range at x={x}: {result}"

    def test_fbm_noise1_equivalent_to_noise2_with_y_zero(self) -> None:
        """test that fbm_noise1 is equivalent to fbm_noise2 with y=0."""
        # given
        init_noise(42)
        x = 0.5
        octaves = 2
        persistence = 0.5

        # when
        value_noise1 = fbm_noise1(x, octaves=octaves, persistence=persistence)
        value_noise2 = fbm_noise2(x, 0.0, octaves=octaves, persistence=persistence)

        # then
        assert value_noise1 == value_noise2
