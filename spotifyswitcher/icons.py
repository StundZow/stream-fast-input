"""Line icons (Feather style: 2-unit stroke, round caps and joins) drawn by hand as SVG
and rendered in the current theme's colours.

They replace every emoji and symbol glyph the interface used, for two reasons: they match
the flat look of the app icon, and the first glyph Segoe UI lacks makes Qt load a fallback
font (Segoe UI Symbol / Emoji) — about 1 s at startup, during which the process is frozen.
With these, every piece of text in the UI is plain Segoe UI.

Icons set on long-lived widgets are bound: a theme change re-renders them in the new
colours. Panels, rebuilt each time they open, simply take the colours of the moment.
"""

from __future__ import annotations

import math
import weakref

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_STROKE = 2.0


def _gear() -> str:
    teeth, r_out, r_in = 8, 9.4, 7.0
    width = math.pi / teeth * 0.52
    points = []
    for i in range(teeth):
        angle = 2 * math.pi * i / teeth
        for radius, offset in ((r_in, -width), (r_out, -width * 0.62), (r_out, width * 0.62), (r_in, width)):
            points.append((12 + radius * math.cos(angle + offset), 12 + radius * math.sin(angle + offset)))
    path = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in points) + " Z"
    return f'<path d="{path}"/><circle cx="12" cy="12" r="3"/>'


def _sun() -> str:
    rays = []
    for i in range(8):
        angle = math.pi / 4 * i
        x1, y1 = 12 + 6.8 * math.cos(angle), 12 + 6.8 * math.sin(angle)
        x2, y2 = 12 + 9.2 * math.cos(angle), 12 + 9.2 * math.sin(angle)
        rays.append(f"M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}")
    return f'<circle cx="12" cy="12" r="4"/><path d="{" ".join(rays)}"/>'


SHAPES = {
    "settings": _gear(),
    "sun": _sun(),
    "moon": '<path d="M20 14.6A8.2 8.2 0 0 1 9.4 4 8.2 8.2 0 1 0 20 14.6z"/>',
    "more": '<circle cx="5.5" cy="12" r="1.1"/><circle cx="12" cy="12" r="1.1"/><circle cx="18.5" cy="12" r="1.1"/>',
    "volume": '<path d="M11 5.5L6.5 9.2H3.5v5.6h3l4.5 3.7z"/><path d="M15.4 9a4.3 4.3 0 0 1 0 6M18.3 6.2a8.2 8.2 0 0 1 0 11.6"/>',
    # LIVE: a broadcast point with its waves; NORMAL: headphones
    "live": '<circle cx="12" cy="12" r="2.2"/>'
    '<path d="M15.8 8.2a5.4 5.4 0 0 1 0 7.6M8.2 15.8a5.4 5.4 0 0 1 0-7.6"/>'
    '<path d="M18.7 5.3a9.5 9.5 0 0 1 0 13.4M5.3 18.7a9.5 9.5 0 0 1 0-13.4"/>',
    "headphones": '<path d="M4 17.5V12a8 8 0 0 1 16 0v5.5"/>'
    '<path d="M20 18a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM4 18a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H4z"/>',
    "check": '<path d="M5 12.6l4.4 4.4L19 7.4"/>',
    "x": '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    "alert": '<path d="M10.3 4.4L2.8 17.6A2 2 0 0 0 4.5 20.6h15a2 2 0 0 0 1.7-3L13.7 4.4a2 2 0 0 0-3.4 0z"/>'
    '<path d="M12 9.5v4.2M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="8.8"/><path d="M12 11v5.2M12 7.6h.01"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.3-4.3"/>',
    "refresh": '<path d="M19.8 11.2A7.9 7.9 0 0 0 6.2 6.4L4.2 8.4"/><path d="M4.2 4.2v4.2h4.2"/>'
    '<path d="M4.2 12.8a7.9 7.9 0 0 0 13.6 4.8l2-2"/><path d="M19.8 19.8v-4.2h-4.2"/>',
    "chevron": '<path d="M6.5 9.5l5.5 5.5 5.5-5.5"/>',
}

# named colour -> palette key
_ROLES = {
    "text": "text",
    "muted": "text_muted",
    "dim": "text_dim",
    "accent": "accent",
    "faded": "faded_text",
    "success": "success_text",
    "warn": "warning_text",
}

_palette: dict = {}
_cache: dict = {}
# widget -> ("icon" | "pixmap", args): re-applied by set_palette on a theme change
_bound: "weakref.WeakKeyDictionary" = weakref.WeakKeyDictionary()


def set_palette(palette: dict):
    """Switch the icons' theme and re-render every bound icon still alive."""
    global _palette
    if palette is _palette:
        return
    _palette = palette
    _cache.clear()
    for widget, (kind, args) in list(_bound.items()):
        try:
            _apply(widget, kind, args)
        except RuntimeError:  # C++ widget already gone
            _bound.pop(widget, None)


def color(role: str) -> str:
    if role.startswith("#"):
        return role
    if role == "white":
        return "#ffffff"
    return _palette.get(_ROLES.get(role, role), "#888888")


def pixmap(name: str, role: str = "text", size: int = 18) -> QPixmap:
    # rendered at the screen's real pixel ratio: no resampling, so strokes stay crisp
    app = QGuiApplication.instance()
    ratio = app.devicePixelRatio() if app else 1.0
    key = (name, color(role), size, ratio)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color(role)}" stroke-width="{_STROKE}" stroke-linecap="round" '
        f'stroke-linejoin="round">{SHAPES[name]}</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    side = round(size * ratio)
    image = QPixmap(side, side)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    image.setDevicePixelRatio(ratio)
    _cache[key] = image
    return image


def icon(name: str, role: str = "text", size: int = 18, checked_role: str | None = None) -> QIcon:
    """QIcon with a dimmed disabled state and, for checkable buttons, a different
    colour when checked."""
    result = QIcon()
    result.addPixmap(pixmap(name, role, size), QIcon.Normal, QIcon.Off)
    result.addPixmap(pixmap(name, checked_role or role, size), QIcon.Normal, QIcon.On)
    result.addPixmap(pixmap(name, "dim", size), QIcon.Disabled, QIcon.Off)
    result.addPixmap(pixmap(name, "dim", size), QIcon.Disabled, QIcon.On)
    return result


def _apply(widget, kind: str, args: tuple):
    if kind == "icon":
        name, role, size, checked_role = args
        widget.setIcon(icon(name, role, size, checked_role))
        widget.setIconSize(QSize(size, size))
    else:
        name, role, size = args
        widget.setPixmap(pixmap(name, role, size))


def bind(widget, name: str, role: str = "text", size: int = 18, checked_role: str | None = None):
    """Sets the button's icon and keeps it, to re-render it on the next theme change."""
    args = (name, role, size, checked_role)
    _apply(widget, "icon", args)
    _bound[widget] = ("icon", args)


def bind_label(label, name: str, role: str = "text", size: int = 18):
    """Same as bind() for a QLabel showing an icon; re-binding replaces the previous one."""
    args = (name, role, size)
    _apply(label, "pixmap", args)
    _bound[label] = ("pixmap", args)


def label(name: str, role: str = "text", size: int = 18):
    """A fixed-size QLabel showing a bound icon."""
    from PySide6.QtWidgets import QLabel

    widget = QLabel()
    widget.setFixedSize(size, size)
    widget.setAlignment(Qt.AlignCenter)
    bind_label(widget, name, role, size)
    return widget
