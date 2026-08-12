from .resources import resource_path

_CHECK_ICON = resource_path("assets/check.png").replace("\\", "/")


def build_stylesheet(p: dict) -> str:
    return f"""
QWidget {{
    background-color: {p['bg']};
    color: {p['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}

QLabel#title {{
    font-size: 21px;
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

QFrame#card {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {p['card_bg_top']}, stop:0.22 {p['card_bg']}, stop:1 {p['card_bg']});
    border-radius: 22px;
    border: 1px solid {p['card_border']};
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
    border-radius: 17px;
    font-size: 19px;
    color: {p['text_muted']};
}}
QPushButton#iconButton:hover {{
    background-color: {p['input_bg']};
}}

/* ---- big LIVE / NORMAL mode buttons ------------------------------------ */
QPushButton#modeButtonLive, QPushButton#modeButtonNormal {{
    background-color: {p['input_bg']};
    border: 1px solid {p['input_border']};
    border-radius: 20px;
    padding: 14px 10px;
    color: {p['text_muted']};
    font-size: 17px;
    font-weight: 700;
}}
QPushButton#modeButtonLive:hover, QPushButton#modeButtonNormal:hover {{
    border-color: {p['input_border_hover']};
    color: {p['text']};
}}
QPushButton#modeButtonLive:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f43f5e, stop:1 #b91c1c);
    border: 1px solid rgba(255,255,255,0.20);
    color: #ffffff;
}}
QPushButton#modeButtonLive:checked:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fb5773, stop:1 #d4231f);
}}
QPushButton#modeButtonNormal:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #22c55e, stop:1 #15803d);
    border: 1px solid rgba(255,255,255,0.20);
    color: #ffffff;
}}
QPushButton#modeButtonNormal:checked:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #34d874, stop:1 #1c9548);
}}

/* ---- status badge (result of the last switch) -------------------------- */
QFrame#statusBadge {{
    border-radius: 16px;
    padding: 4px;
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
    background-color: {p['input_bg']};
    border: 1px solid {p['input_border']};
}}
QLabel#statusBadgeText[kind="success"] {{
    color: {p['success_text']};
    font-weight: 600;
    font-size: 12px;
}}
QLabel#statusBadgeText[kind="warning"] {{
    color: {p['warning_text']};
    font-weight: 600;
    font-size: 12px;
}}
QLabel#statusBadgeText[kind="idle"] {{
    color: {p['text_dim']};
    font-weight: 600;
    font-size: 12px;
}}

QFrame#modalCard {{
    background-color: {p['modal_card_bg']};
    border-radius: 22px;
    border: 1px solid {p['card_border']};
}}

QPushButton#pathButton {{
    background-color: {p['input_bg']};
    border: 1px solid {p['input_border']};
    border-radius: 14px;
    padding: 9px 18px;
    color: {p['text']};
    font-weight: 600;
}}
QPushButton#pathButton:hover {{
    background-color: {p['input_border']};
    border-color: {p['input_border_hover']};
}}

/* ---- device picker: a custom-drawn dropdown, not native QComboBox ------ */
QFrame#devicePickerButton {{
    background-color: {p['input_bg']};
    border: 1px solid {p['input_border']};
    border-radius: 13px;
    font-size: 13px;
}}
QFrame#devicePickerButton:hover {{
    border-color: {p['input_border_hover']};
}}

QFrame#devicePopup {{
    background-color: {p['modal_card_bg']};
    border: 1px solid {p['input_border_hover']};
    border-radius: 16px;
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
    border-radius: 10px;
}}
QListWidget#devicePopupList::item:hover {{
    background-color: {p['input_bg']};
}}
QListWidget#devicePopupList::item:selected {{
    background-color: {p['pin_toggle_checked_bg']};
    border: 1px solid {p['pin_toggle_checked_border']};
    color: {p['text']};
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
    padding: 4px 8px;
    text-decoration: underline;
}}
QPushButton#debugButton:hover {{
    color: {p['text_muted']};
}}

/* ---- theme toggle (sun/moon), reused from Rec Size Helper -------------- */
QFrame#segmentIconPill {{
    background-color: {p['input_bg']};
    border: 1px solid {p['input_border']};
    border-radius: 17px;
}}
QPushButton#segmentIconItem {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 13px;
    padding: 4px 11px;
    font-size: 15px;
    color: {p['text_muted']};
}}
QPushButton#segmentIconItem:hover {{
    color: {p['text']};
}}
QFrame#segmentIconThumb {{
    background-color: {p['pin_toggle_checked_bg']};
    border: 1px solid {p['pin_toggle_checked_border']};
    border-radius: 13px;
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: {p['scrollbar_bg']};
    width: 10px;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {p['scrollbar_handle']};
    border-radius: 4px;
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
