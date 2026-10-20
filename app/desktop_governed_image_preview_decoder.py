"""Bounded JPEG-to-PNG decoder for governed desktop previews."""

from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError


def decode_governed_jpeg_preview(
    payload: bytes,
    content_type: str,
    *,
    max_pixels: int = 16_000_000,
    max_dimension: int = 8192,
    preview_width: int = 800,
    preview_height: int = 600,
) -> bytes | None:
    """Return bounded PNG bytes or decline an invalid JPEG."""
    if not isinstance(payload, bytes):
        return None
    if not isinstance(content_type, str):
        return None
    if content_type.casefold() != "image/jpeg":
        return None
    if not payload or len(payload) > 1_000_000:
        return None
    if not payload.startswith(bytes.fromhex("ffd8")):
        return None

    limits = (
        max_pixels,
        max_dimension,
        preview_width,
        preview_height,
    )
    if any(type(limit) is not int or limit <= 0 for limit in limits):
        return None

    try:
        with Image.open(BytesIO(payload)) as image:
            if image.format != "JPEG":
                return None

            width, height = image.size
            if width <= 0 or height <= 0:
                return None
            if width > max_dimension or height > max_dimension:
                return None
            if width * height > max_pixels:
                return None

            image.draft("RGB", (preview_width, preview_height))
            image.load()
            image.thumbnail(
                (preview_width, preview_height),
                Image.Resampling.LANCZOS,
            )

            if image.mode != "RGB":
                image = image.convert("RGB")

            output = BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()

    except (
        OSError,
        ValueError,
        SyntaxError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ):
        return None
