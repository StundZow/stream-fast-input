from .theme import BLUE, TEAL

# The app icon's tile, as a fill: teal top-left -> blue bottom-right.
_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {TEAL}, stop:1 {BLUE})"
_GRADIENT_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3CDDD0, stop:1 #4670F0)"


def build_stylesheet(p: dict) -> str:
    # 'Segoe UI' alone, no generic fallback: a generic family such as sans-serif makes
    # Qt resolve the system fallback chain the first time text is shaped — ~1 s, once,
    # with the thread frozen (measured). Segoe UI ships with every Windows 10/11.
    return f"""
QWidget {{
    background-color: transparent;
    color: {p['text']};
    font-family: 'Segoe UI';
    font-size: 13px;
}}

QLabel#title {{
    font-size: 20px;
    font-weight: 700;
    color: {p['text']};
}}

QLabel#subtitle {{
    color: {p['text_muted']};
    font-size: 12px;
}}

QLabel#mutedText {{
    color: {p['text_muted']};
}}

QLabel#dimText {{
    color: {p['text_dim']};
    font-size: 11px;
}}

QLabel#sectionTitle {{
    font-weight: 600;
    font-size: 13px;
}}

QFrame#card {{
    background-color: {p['surface']};
    border: 1px solid {p['surface_border']};
    border-radius: 16px;
}}

QLabel#cardTitle {{
    font-size: 15px;
    font-weight: 700;
    color: {p['text']};
}}

QLabel#statusValue {{
    font-size: 13px;
    font-weight: 600;
    color: {p['text']};
}}

QPushButton#iconButton {{
    background: transparent;
    border: none;
    border-radius: 10px;
}}
QPushButton#iconButton:hover {{
    background-color: {p['control_hover']};
}}
QPushButton#iconButton:pressed {{
    background-color: {p['control_border']};
}}

/* ---- LIVE / NORMAL: the active output solid, the other faded (the logo's idea) ---- */
QPushButton#modeButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {p['faded_a']}, stop:1 {p['faded_b']});
    border: 1px solid {p['faded_border']};
    border-radius: 18px;
    padding: 0 12px;
    color: {p['faded_text']};
    font-size: 17px;
    font-weight: 700;
}}
QPushButton#modeButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {p['faded_hover_a']}, stop:1 {p['faded_hover_b']});
    border-color: {p['faded_border_hover']};
    color: {p['faded_text_hover']};
}}
QPushButton#modeButton:checked {{
    background: {_GRADIENT};
    border: 1px solid transparent;
    color: #ffffff;
}}
QPushButton#modeButton:checked:hover {{
    background: {_GRADIENT_HOVER};
}}

/* ---- status badge (result of the last switch) -------------------------- */
QFrame#statusBadge {{
    border-radius: 12px;
}}
QFrame#statusBadge[kind="success"] {{
    background-color: {p['success_bg']};
    border: 1px solid {p['success_border']};
}}
QFrame#statusBadge[kind="warning"] {{
    background-color: {p['warning_bg']};
    border: 1px solid {p['warning_border']};
}}
QFrame#statusBadge[kind="idle"] {{
    background-color: {p['surface']};
    border: 1px solid {p['surface_border']};
}}
QLabel#statusBadgeText {{
    font-weight: 600;
    font-size: 12px;
}}
QLabel#statusBadgeText[kind="success"] {{
    color: {p['success_text']};
}}
QLabel#statusBadgeText[kind="warning"] {{
    color: {p['warning_text']};
}}
QLabel#statusBadgeText[kind="idle"] {{
    color: {p['text_muted']};
}}

QFrame#modalCard {{
    background-color: {p['elevated']};
    border-radius: 18px;
    border: 1px solid {p['elevated_border']};
}}

QPushButton#pathButton {{
    background-color: {p['control_bg']};
    border: 1px solid {p['control_border']};
    border-radius: 12px;
    padding: 8px 16px;
    color: {p['text']};
    font-weight: 600;
}}
QPushButton#pathButton:hover {{
    background-color: {p['control_hover']};
    border-color: {p['control_border_hover']};
}}
QPushButton#pathButton:disabled {{
    color: {p['text_dim']};
}}

/* ---- device picker: a custom-drawn dropdown, not native QComboBox ------ */
QFrame#devicePickerButton {{
    background-color: {p['control_bg']};
    border: 1px solid {p['control_border']};
    border-radius: 12px;
    font-size: 13px;
}}
QFrame#devicePickerButton:hover {{
    border-color: {p['control_border_hover']};
}}

QFrame#devicePopup {{
    background-color: {p['elevated']};
    border: 1px solid {p['elevated_border']};
    border-radius: 14px;
}}
QListWidget#devicePopupList {{
    background: transparent;
    border: none;
    outline: none;
    color: {p['text']};
    font-size: 13px;
}}
QListWidget#devicePopupList::item {{
    padding: 10px 14px;
    margin: 1px 2px;
    border-radius: 9px;
}}
QListWidget#devicePopupList::item:hover {{
    background-color: {p['control_hover']};
}}
QListWidget#devicePopupList::item:selected {{
    background: {_GRADIENT};
    color: #ffffff;
    font-weight: 600;
}}
QListWidget#devicePopupList::corner {{
    background: transparent;
}}

QPushButton#debugButton {{
    background: transparent;
    border: none;
    color: {p['text_dim']};
    font-size: 11px;
    padding: 4px 6px;
}}
QPushButton#debugButton:hover {{
    color: {p['text_muted']};
}}

/* ---- two-icon switches (theme, Voicemeeter): the active side solid ----- */
QFrame#segmentIconPill {{
    background-color: {p['control_bg']};
    border: 1px solid {p['control_border']};
    border-radius: 17px;
}}
QPushButton#segmentIconItem {{
    background: transparent;
    border: none;
    border-radius: 13px;
}}
QFrame#segmentIconThumb {{
    background: {_GRADIENT};
    border: none;
    border-radius: 13px;
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: transparent;
    width: 10px;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {p['scrollbar_handle']};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
    width: 0px;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}
"""
