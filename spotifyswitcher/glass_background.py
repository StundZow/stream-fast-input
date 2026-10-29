from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget

from .theme import DARK


class GlassBackground(QWidget):
    """Window backdrop: a flat base with two faint washes, teal top-left and blue
    bottom-right — the app icon's gradient direction, kept low enough that the solid
    cards above stay crisp and contrasted."""

    # (rel_x, rel_y, rel_radius) — radius as a fraction of the larger window dimension
    _HALO_LAYOUT = [
        (0.0, 0.0, 0.85),
        (1.0, 1.0, 0.95),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette = DARK

    def set_theme(self, palette: dict):
        self._palette = palette
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        base = QLinearGradient(QPointF(0, 0), QPointF(rect.width(), rect.height()))
        base.setColorAt(0.0, QColor(self._palette["bg_base"]))
        base.setColorAt(1.0, QColor(self._palette["bg_base2"]))
        painter.fillRect(rect, base)

        span = max(rect.width(), rect.height())
        alpha = self._palette["halo_alpha"]
        for (rx, ry, rr), color_hex in zip(self._HALO_LAYOUT, self._palette["halo_colors"]):
            gradient = QRadialGradient(QPointF(rect.width() * rx, rect.height() * ry), span * rr)
            color = QColor(color_hex)
            color.setAlpha(alpha)
            edge = QColor(color_hex)
            edge.setAlpha(0)
            gradient.setColorAt(0.0, color)
            gradient.setColorAt(1.0, edge)
            painter.fillRect(rect, gradient)

        painter.end()
