from __future__ import annotations

import re
import winreg

from PySide6.QtGui import QColor

DARK = {
    "name": "dark",
    "bg_base": "#151024",
    "bg_base2": "#1c1533",
    "blob_colors": ["#7c3aed", "#db2777", "#2563eb", "#0d9488"],
    "blob_alpha": 78,
    "bg": "rgba(0,0,0,0)",
    "card_bg": "rgba(32,26,54,0.38)",
    "card_bg_top": "rgba(52,44,82,0.46)",
    "card_border": "rgba(255,255,255,0.10)",
    "text": "#f4f1fb",
    "text_muted": "#b6adcf",
    "text_dim": "#8d84a6",
    "input_bg": "rgba(255,255,255,0.07)",
    "input_border": "rgba(255,255,255,0.12)",
    "input_border_hover": "rgba(255,255,255,0.25)",
    "pin_toggle_checked_bg": "rgba(139,92,246,0.25)",
    "pin_toggle_checked_border": "rgba(167,139,250,0.55)",
    "success_bg": "rgba(34,197,94,0.15)",
    "success_border": "rgba(74,222,128,0.32)",
    "success_text": "#bbf7d0",
    "warning_bg": "rgba(251,191,36,0.15)",
    "warning_border": "rgba(252,211,77,0.32)",
    "warning_text": "#fde68a",
    "modal_card_bg": "#241a3d",
    "scrollbar_bg": "rgba(255,255,255,0.05)",
    "scrollbar_handle": "rgba(255,255,255,0.24)",
}

LIGHT = {
    "name": "light",
    "bg_base": "#f7f3fd",
    "bg_base2": "#edf2fd",
    "blob_colors": ["#a78bfa", "#f472b6", "#60a5fa", "#2dd4bf"],
    "blob_alpha": 105,
    "bg": "rgba(0,0,0,0)",
    "card_bg": "rgba(255,255,255,0.24)",
    "card_bg_top": "rgba(255,255,255,0.34)",
    "card_border": "rgba(255,255,255,0.42)",
    "text": "#241f38",
    "text_muted": "#665d84",
    "text_dim": "#9d93ba",
    "input_bg": "rgba(255,255,255,0.38)",
    "input_border": "rgba(255,255,255,0.60)",
    "input_border_hover": "rgba(255,255,255,0.90)",
    "pin_toggle_checked_bg": "rgba(139,92,246,0.16)",
    "pin_toggle_checked_border": "rgba(139,92,246,0.45)",
    "success_bg": "rgba(34,197,94,0.16)",
    "success_border": "rgba(22,163,74,0.35)",
    "success_text": "#166534",
    "warning_bg": "rgba(251,191,36,0.20)",
    "warning_border": "rgba(217,119,6,0.35)",
    "warning_text": "#92400e",
    "modal_card_bg": "#ffffff",
    "scrollbar_bg": "rgba(90,70,130,0.10)",
    "scrollbar_handle": "rgba(120,100,160,0.45)",
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
