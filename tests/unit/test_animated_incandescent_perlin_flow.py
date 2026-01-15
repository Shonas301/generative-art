"""Unit tests for animated_incandescent_perlin_flow module."""

import pytest

from generative_art.animated_incandescent_perlin_flow import parse_resolution


def test_parse_resolution_with_1080p_shorthand() -> None:
    """test that 1080p shorthand resolves to correct dimensions."""
    # given
    resolution_str = "1080p"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (1920, 1080)


def test_parse_resolution_with_4k_shorthand() -> None:
    """test that 4k shorthand resolves to correct dimensions."""
    # given
    resolution_str = "4k"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (3840, 2160)


def test_parse_resolution_with_1440p_shorthand() -> None:
    """test that 1440p shorthand resolves to correct dimensions."""
    # given
    resolution_str = "1440p"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (2560, 1440)


def test_parse_resolution_with_720p_shorthand() -> None:
    """test that 720p shorthand resolves to correct dimensions."""
    # given
    resolution_str = "720p"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (1280, 720)


def test_parse_resolution_with_portrait_shorthand() -> None:
    """test that portrait shorthands resolve to correct dimensions."""
    # given
    resolution_str = "1440p_portrait"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (1440, 2560)


def test_parse_resolution_with_qhd_portrait_shorthand() -> None:
    """test that qhd_portrait shorthand resolves to correct dimensions."""
    # given
    resolution_str = "qhd_portrait"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (1440, 2560)


def test_parse_resolution_with_case_insensitive_shorthand() -> None:
    """test that shorthand parsing is case-insensitive."""
    # given
    resolution_str = "4K"  # uppercase

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (3840, 2160)


def test_parse_resolution_with_custom_format() -> None:
    """test that custom WIDTHxHEIGHT format works."""
    # given
    resolution_str = "1920x1080"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (1920, 1080)


def test_parse_resolution_with_custom_format_4k() -> None:
    """test that custom format works for 4k dimensions."""
    # given
    resolution_str = "3840x2160"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (3840, 2160)


def test_parse_resolution_with_custom_odd_dimensions() -> None:
    """test that custom format works for non-standard dimensions."""
    # given
    resolution_str = "2560x1600"

    # when
    result = parse_resolution(resolution_str)

    # then
    assert result == (2560, 1600)


def test_parse_resolution_raises_error_for_invalid_string() -> None:
    """test that invalid resolution string raises ValueError."""
    # given
    invalid_resolution = "invalid"

    # when/then
    with pytest.raises(ValueError) as exc_info:
        parse_resolution(invalid_resolution)

    # then
    assert "invalid resolution: 'invalid'" in str(exc_info.value)
    assert "use shorthand" in str(exc_info.value)


def test_parse_resolution_raises_error_for_malformed_custom_format() -> None:
    """test that malformed custom format raises ValueError."""
    # given
    malformed_resolution = "1920-1080"  # wrong separator

    # when/then
    with pytest.raises(ValueError) as exc_info:
        parse_resolution(malformed_resolution)

    # then
    assert "invalid resolution" in str(exc_info.value)


def test_parse_resolution_raises_error_for_negative_dimensions() -> None:
    """test that negative dimensions raise ValueError."""
    # given
    negative_resolution = "-1920x1080"

    # when/then
    with pytest.raises(ValueError) as exc_info:
        parse_resolution(negative_resolution)

    # then
    assert "invalid resolution" in str(exc_info.value)


def test_parse_resolution_raises_error_for_zero_dimensions() -> None:
    """test that zero dimensions raise ValueError."""
    # given
    zero_resolution = "0x0"

    # when/then
    with pytest.raises(ValueError) as exc_info:
        parse_resolution(zero_resolution)

    # then
    assert "invalid resolution" in str(exc_info.value)


def test_parse_resolution_raises_error_for_non_numeric_dimensions() -> None:
    """test that non-numeric dimensions raise ValueError."""
    # given
    non_numeric_resolution = "widthxheight"

    # when/then
    with pytest.raises(ValueError) as exc_info:
        parse_resolution(non_numeric_resolution)

    # then
    assert "invalid resolution" in str(exc_info.value)
