"""Boundary tests for governed JPEG preview decoding."""

from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from app.desktop_governed_image_preview_decoder import (
    decode_governed_jpeg_preview,
)


def make_jpeg(width=64, height=48):
    image = Image.new("RGB", (width, height), "red")
    output = BytesIO()
    image.save(output, format="JPEG")
    return output.getvalue()


def test_truncated_jpeg_is_rejected():
    payload = make_jpeg()
    assert decode_governed_jpeg_preview(payload[:-20], "image/jpeg") is None


def test_payload_over_one_megabyte_is_rejected():
    payload = make_jpeg()
    oversized = payload + b"X" * (1_000_001 - len(payload))
    assert len(oversized) == 1_000_001
    assert decode_governed_jpeg_preview(oversized, "image/jpeg") is None


def test_dimension_limit_is_enforced():
    payload = make_jpeg(120, 80)
    assert (
        decode_governed_jpeg_preview(payload, "image/jpeg", max_dimension=100) is None
    )


def test_pixel_limit_is_enforced():
    payload = make_jpeg(120, 80)
    assert decode_governed_jpeg_preview(payload, "image/jpeg", max_pixels=9_000) is None


@pytest.mark.parametrize(
    "parameter",
    (
        {"max_pixels": 0},
        {"max_dimension": -1},
        {"preview_width": 0},
        {"preview_height": -1},
        {"max_pixels": True},
    ),
)
def test_invalid_limits_are_rejected(parameter):
    assert decode_governed_jpeg_preview(make_jpeg(), "image/jpeg", **parameter) is None


def test_large_valid_jpeg_is_reduced():
    payload = make_jpeg(1600, 1200)
    converted = decode_governed_jpeg_preview(payload, "image/jpeg")

    assert isinstance(converted, bytes)
    assert converted.startswith(bytes.fromhex("89504e470d0a1a0a"))

    with Image.open(BytesIO(converted)) as image:
        assert image.format == "PNG"
        assert image.width <= 800
        assert image.height <= 600
