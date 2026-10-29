"""Generates the app icon from its vector drawing (the SVG below): `icon.ico` with every size
Windows asks for (at the repo root for StreamFastInput.spec, which embeds it in the exe, and in
spotifyswitcher/assets/ for the window), `spotifyswitcher/assets/icon.png` (launch screen) and
`newicon.png` (README).

The drawing: a full-bleed tile with a teal -> blue gradient and a white glyph, an audio wave
forking into two outputs, the active one solid and the other faded: the LIVE / NORMAL switch.
Up to 24 px a simplified variant (straight input, thicker strokes, edge-to-edge tile) stays
crisp. Re-run after any change to the drawing:

    python tools/make_icon.py
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "spotifyswitcher" / "assets"

TOP_LEFT, BOTTOM_RIGHT = "#22D3C5", "#2F5BEA"
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
SMALL_MAX = 24
PNG_SIZE = 512

# Faded parts are painted with the tile gradient lightened (url(#w45): mixed with 45% white)
# instead of translucent white, so where two of them overlap nothing shows.
ICON = """
<path d="M470 512 C560 512 580 694 670 694" fill="none" stroke="url(#w45)" stroke-width="84" stroke-linecap="round"/>
<circle cx="782" cy="694" r="62" fill="none" stroke="url(#w45)" stroke-width="52"/>
<path d="M190 512 C232 404 274 404 316 512 S400 620 442 512 L470 512 C560 512 580 330 670 330" fill="none" stroke="#fff" stroke-width="84" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="782" cy="330" r="90" fill="#fff"/>
"""

SMALL = """
<path d="M450 512 C560 512 580 700 700 700 L740 700" fill="none" stroke="url(#w45)" stroke-width="112" stroke-linecap="round"/>
<circle cx="770" cy="700" r="80" fill="url(#w45)"/>
<path d="M210 512 L450 512 C560 512 580 324 700 324 L740 324" fill="none" stroke="#fff" stroke-width="112" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="770" cy="324" r="104" fill="#fff"/>
"""


def lighten(color: str, amount: float) -> str:
    rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(c + (255 - c) * amount):02x}" for c in rgb)


def gradient(gid: str, start: str, end: str, inset: int) -> str:
    far = 1024 - inset
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{inset}" y1="{inset}" x2="{far}" y2="{far}">'
        f'<stop offset="0" stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient>'
    )


def svg(glyph: str, inset: int = 32) -> str:
    """The tile (rounded square, diagonal gradient), the glyph, then a soft top-left sheen
    laid over everything."""
    tints = "".join(
        gradient(f"w{p}", lighten(TOP_LEFT, int(p) / 100), lighten(BOTTOM_RIGHT, int(p) / 100), inset)
        for p in sorted(set(re.findall(r"url\(#w(\d+)\)", glyph)))
    )
    side = 1024 - 2 * inset
    radius = round(side * 0.233)
    tile = f'<rect x="{inset}" y="{inset}" width="{side}" height="{side}" rx="{radius}"'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><defs>
{gradient("bg", TOP_LEFT, BOTTOM_RIGHT, inset)}{tints}
<radialGradient id="sheen" gradientUnits="userSpaceOnUse" cx="260" cy="120" r="900">
<stop offset="0" stop-color="#fff" stop-opacity="0.16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient></defs>
{tile} fill="url(#bg)"/>{glyph}{tile} fill="url(#sheen)"/></svg>"""


def render(svg_text: str, size: int) -> QImage:
    image = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(svg_text.encode())).render(painter, QRectF(0, 0, size, size))
    painter.end()
    return image.convertToFormat(QImage.Format_ARGB32)


def png_bytes(image: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def dib_bytes(image: QImage) -> bytes:
    """32-bit BGRA bitmap (bottom-up rows) followed by the AND mask: the classic .ico frame
    format, readable by anything that reads icons at all."""
    size = image.width()
    stride = size * 4
    pixels = bytes(image.constBits())[: stride * size]
    rows = [pixels[y * stride:(y + 1) * stride] for y in reversed(range(size))]
    mask_stride = (size + 31) // 32 * 4
    mask = bytearray()
    for row in rows:
        bits = bytearray(mask_stride)
        for x in range(size):
            if row[x * 4 + 3] == 0:
                bits[x // 8] |= 0x80 >> (x % 8)
        mask += bits
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, stride * size + len(mask), 0, 0, 0, 0)
    return header + b"".join(rows) + bytes(mask)


def write_ico(path: Path, frames: list[QImage]) -> None:
    # 256 px as PNG (the only format Windows expects at that size), smaller frames as bitmaps
    blobs = [png_bytes(f) if f.width() >= 256 else dib_bytes(f) for f in frames]
    offset = 6 + 16 * len(frames)
    entries = b""
    for frame, blob in zip(frames, blobs):
        side = frame.width() % 256  # 256 is stored as 0
        entries += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    path.write_bytes(struct.pack("<HHH", 0, 1, len(frames)) + entries + b"".join(blobs))


def main() -> None:
    QGuiApplication(sys.argv)
    icon, small = svg(ICON), svg(SMALL, inset=0)
    frames = [render(small if size <= SMALL_MAX else icon, size) for size in ICO_SIZES]
    for path in (ROOT / "icon.ico", ASSETS / "icon.ico"):
        write_ico(path, frames)
        print(f"{path.relative_to(ROOT)}: {', '.join(map(str, ICO_SIZES))} px")
    image = render(icon, PNG_SIZE)
    for path in (ASSETS / "icon.png", ROOT / "newicon.png"):
        image.save(str(path))
        print(f"{path.relative_to(ROOT)}: {PNG_SIZE}x{PNG_SIZE}")


if __name__ == "__main__":
    main()
