"""
Compose a shareable outfit card image.
"""

from __future__ import annotations

import asyncio
from io import BytesIO

import httpx
from PIL import Image, ImageDraw, ImageFont

_CELL_SIZE = 400
_CANVAS_SIZE = 800
_GRID_POSITIONS = [(0, 0), (_CELL_SIZE, 0), (0, _CELL_SIZE), (_CELL_SIZE, _CELL_SIZE)]


def _placeholder_tile(label: str | None = None) -> Image.Image:
    tile = Image.new("RGB", (_CELL_SIZE, _CELL_SIZE), (232, 232, 232))
    draw = ImageDraw.Draw(tile)
    draw.rectangle([(16, 16), (_CELL_SIZE - 16, _CELL_SIZE - 16)], outline=(170, 170, 170), width=2)
    text = (label or "Image unavailable")[:40]
    draw.text((24, _CELL_SIZE - 40), text, fill=(110, 110, 110))
    return tile


def _fit_image_to_cell(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    tile = Image.new("RGB", (_CELL_SIZE, _CELL_SIZE), (246, 246, 246))
    image.thumbnail((_CELL_SIZE - 24, _CELL_SIZE - 24), Image.Resampling.LANCZOS)
    x = (_CELL_SIZE - image.width) // 2
    y = (_CELL_SIZE - image.height) // 2
    tile.paste(image, (x, y))
    return tile


async def _download_tile(client: httpx.AsyncClient, item: dict) -> Image.Image:
    image_url = item.get("image_url")
    label = f"{item.get('category') or 'Item'} - {item.get('colour') or 'n/a'}"
    if not image_url:
        return _placeholder_tile(label)
    try:
        response = await client.get(str(image_url))
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        tile = _fit_image_to_cell(image)
    except Exception:
        tile = _placeholder_tile(label)

    draw = ImageDraw.Draw(tile)
    draw.rectangle([(0, _CELL_SIZE - 28), (_CELL_SIZE, _CELL_SIZE)], fill=(255, 255, 255))
    draw.text((8, _CELL_SIZE - 22), label[:44], fill=(80, 80, 80))
    return tile


async def compose_outfit_card(outfit_items: list[dict]) -> bytes:
    """
    Build an 800x800 PNG card from up to four outfit item images.
    """
    items = list(outfit_items[:4])
    while len(items) < 4:
        items.append({})

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        tiles = await asyncio.gather(*[_download_tile(client, item) for item in items])

    canvas = Image.new("RGB", (_CANVAS_SIZE, _CANVAS_SIZE), (255, 255, 255))
    for tile, (x, y) in zip(tiles, _GRID_POSITIONS):
        canvas.paste(tile, (x, y))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    watermark = "ModeOn"
    w, h = draw.textbbox((0, 0), watermark, font=font)[2:]
    draw.text((_CANVAS_SIZE - w - 14, _CANVAS_SIZE - h - 12), watermark, fill=(120, 120, 120), font=font)

    output = BytesIO()
    canvas.save(output, format="PNG")
    return output.getvalue()


