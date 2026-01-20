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
