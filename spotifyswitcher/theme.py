from __future__ import annotations

import re
import winreg

from PySide6.QtGui import QColor

# The app icon's gradient (tools/make_icon.py): teal top-left -> blue bottom-right.
TEAL = "#22D3C5"
BLUE = "#2F5BEA"

DARK = {
    "name": "dark",
    "bg_base": "#0A1020",
    "bg_base2": "#0D1529",
    "halo_colors": [TEAL, BLUE],
    "halo_alpha": 34,
    "surface": "#111A2D",
    "surface_border": "#1E2A42",
    "elevated": "#152036",
    "elevated_border": "#283756",
    "text": "#EAF1FA",
    "text_muted": "#93A3BA",
    "text_dim": "#62738D",
    "control_bg": "#172238",
    "control_hover": "#1D2A45",
    "control_border": "#283754",
    "control_border_hover": "#3D5276",
    "accent": TEAL,
    # the inactive LIVE / NORMAL button: the active gradient, faded
    "faded_a": "rgba(34,211,197,0.09)",
    "faded_b": "rgba(47,91,234,0.13)",
    "faded_hover_a": "rgba(34,211,197,0.15)",
    "faded_hover_b": "rgba(47,91,234,0.20)",
    "faded_border": "rgba(70,130,220,0.30)",
    "faded_border_hover": "rgba(70,150,230,0.50)",
    "faded_text": "#7F9CC0",
    "faded_text_hover": "#B3CAE6",
    "success_bg": "rgba(34,211,197,0.10)",
    "success_border": "rgba(34,211,197,0.36)",
    "success_text": "#6FE3D8",
    "warning_bg": "rgba(251,191,36,0.10)",
    "warning_border": "rgba(251,191,36,0.34)",
    "warning_text": "#F7CD62",
    "groove": "#1E2A43",
    "scrollbar_handle": "#2D3C5A",
    "backdrop": (2, 6, 16, 120),
}

LIGHT = {
    "name": "light",
    "bg_base": "#F2F6FB",
    "bg_base2": "#E8EFF8",
    "halo_colors": [TEAL, BLUE],
    "halo_alpha": 28,
    "surface": "#FFFFFF",
    "surface_border": "#DAE3EE",
    "elevated": "#FFFFFF",
    "elevated_border": "#CFDAE8",
    "text": "#0E1A2C",
    "text_muted": "#4E5E74",
    "text_dim": "#8494A9",
    "control_bg": "#F4F8FC",
    "control_hover": "#EAF1F9",
    "control_border": "#D2DCE8",
    "control_border_hover": "#A6BAD2",
    "accent": BLUE,
    "faded_a": "rgba(34,211,197,0.10)",
    "faded_b": "rgba(47,91,234,0.11)",
    "faded_hover_a": "rgba(34,211,197,0.17)",
    "faded_hover_b": "rgba(47,91,234,0.18)",
    "faded_border": "rgba(47,91,234,0.22)",
    "faded_border_hover": "rgba(47,91,234,0.40)",
    "faded_text": "#5A76A0",
    "faded_text_hover": "#2F4F86",
    "success_bg": "rgba(34,211,197,0.13)",
    "success_border": "rgba(13,148,136,0.36)",
    "success_text": "#0B7A70",
    "warning_bg": "rgba(251,191,36,0.15)",
    "warning_border": "rgba(217,119,6,0.38)",
    "warning_text": "#8A4B06",
    "groove": "#DAE3EE",
    "scrollbar_handle": "#B7C5D6",
    "backdrop": (10, 22, 44, 110),
}


def detect_windows_theme() -> str:
    """Return 'light' or 'dark' based on the current Windows apps theme setting."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except OSError:
        return "dark"


def get_palette(name: str) -> dict:
    return LIGHT if name == "light" else DARK


def qcolor(value: str) -> QColor:
    """QColor(str) only understands hex/named colors, not the CSS rgba()/rgb()
    syntax our palettes use for translucency — parse that case manually."""
    if value.startswith("rgba") or value.startswith("rgb"):
        nums = re.findall(r"[\d.]+", value)
        r, g, b = int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
        a = int(round(float(nums[3]) * 255)) if len(nums) > 3 else 255
        return QColor(r, g, b, a)
    return QColor(value)
