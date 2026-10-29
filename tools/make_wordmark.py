"""Renders the splash wordmark once per theme, at 2x, into spotifyswitcher/assets/.

The splash never draws text (that would make it pay the Windows font database like the
app does), so the app name is shipped as an image: "Stream Fast" in the theme's text
colour, "Input" in the app icon's teal -> blue gradient. Re-run after changing the name,
the font, or the palette:

    python tools/make_wordmark.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPen,
)

from spotifyswitcher import theme
from spotifyswitcher.resources import resource_path

SCALE = 2
POINT_SIZE = 26
LEFT, RIGHT = "Stream Fast ", "Input"
PAD = 4


def render(name: str) -> None:
    palette = theme.get_palette(name)
    font = QFont("Segoe UI", POINT_SIZE * SCALE, QFont.Bold)
    metrics = QFontMetrics(font)
    w_left = metrics.horizontalAdvance(LEFT)
    w_right = metrics.horizontalAdvance(RIGHT)
    width = w_left + w_right + 2 * PAD * SCALE
    height = metrics.height() + 2 * PAD * SCALE

    image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.setFont(font)

    x = PAD * SCALE
    baseline = PAD * SCALE + metrics.ascent()
    painter.setPen(QColor(palette["text"]))
    painter.drawText(QPointF(x, baseline), LEFT)

    gradient = QLinearGradient(QPointF(x + w_left, 0), QPointF(x + w_left + w_right, 0))
    gradient.setColorAt(0.0, QColor(theme.TEAL))
    gradient.setColorAt(1.0, QColor(theme.BLUE))
    painter.setPen(QPen(gradient, 1))
    painter.drawText(QPointF(x + w_left, baseline), RIGHT)
    painter.end()

    out = resource_path(f"assets/wordmark_{name}.png")
    image.save(out)
    print(f"{out}  {image.width()}x{image.height()} (logical {image.width() // SCALE}x{image.height() // SCALE})")


def main() -> None:
    QGuiApplication(sys.argv)
    for name in ("dark", "light"):
        render(name)


if __name__ == "__main__":
    main()
