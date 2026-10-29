from __future__ import annotations

from PySide6.QtCore import QPoint, QRectF, Qt, Signal
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from . import icons

_MAX_VISIBLE_ITEMS = 7
_ROW_HEIGHT = 40


class DevicePicker(QFrame):
    """A styled stand-in for a native combo box: click to open a floating
    glass list of audio devices, pick one. Built from scratch instead of
    QComboBox because on Windows that widget's popup renders with native,
    unstyleable chrome that clashes with the rest of the app."""

    changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("devicePickerButton")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self._items: list[str] = []
        self._value: str = ""
        self._popup: QFrame | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 12, 10)
        self._label = QLabel("Sélectionner…")
        layout.addWidget(self._label, stretch=1)
        layout.addWidget(icons.label("chevron", "muted", 16))

    def set_items(self, items: list[str]):
        self._items = list(items)

    def current_text(self) -> str:
        return self._value

    def set_current_text(self, value: str):
        self._value = value
        self._label.setText(value or "Sélectionner…")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_popup()
            # Accept it: an unaccepted QMouseEvent propagates up to the
            # parent chain in Qt, which — since this picker lives inside
            # the Settings overlay's card — reached the overlay itself and
            # was read as "clicked outside the card", closing the whole
            # panel on the very click meant to open the dropdown.
            event.accept()
        else:
            super().mousePressEvent(event)

    def toggle_popup(self):
        if self._popup is not None:
            self._popup.close()
            return
        self._open_popup()

    def _open_popup(self):
        popup = QFrame(self, Qt.Popup | Qt.FramelessWindowHint)
        popup.setAttribute(Qt.WA_StyledBackground, True)
        popup.setAttribute(Qt.WA_DeleteOnClose)
        popup.setObjectName("devicePopup")
        # a fresh top-level window doesn't reliably re-inherit the app-wide
        # stylesheet on first show (Qt.Popup windows are prone to painting
        # before the cascade catches up) — apply it explicitly so the glass
        # look never flashes as an unstyled native list.
        app = QApplication.instance()
        if app:
            popup.setStyleSheet(app.styleSheet())
        popup.destroyed.connect(self._on_popup_destroyed)

        outer = QVBoxLayout(popup)
        outer.setContentsMargins(6, 6, 6, 6)

        listw = QListWidget()
        listw.setObjectName("devicePopupList")
        listw.setFrameShape(QFrame.NoFrame)
        listw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # default is per-item scrolling, which jumps a whole row at a time
        # and feels jerky with a mouse wheel — pixel scrolling is smooth.
        listw.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        items = list(self._items)
        if self._value and self._value not in items:
            items.insert(0, self._value)
        if not items:
            items = ["Aucun périphérique détecté"]

        current_item = None
        for name in items:
            item = QListWidgetItem(name)
            listw.addItem(item)
            if name == self._value:
                current_item = item
        if current_item is not None:
            listw.setCurrentItem(current_item)

        listw.itemClicked.connect(lambda item: self._select(item.text()))
        outer.addWidget(listw)

        visible = max(1, min(len(items), _MAX_VISIBLE_ITEMS))
        list_height = visible * _ROW_HEIGHT + 8
        listw.setFixedHeight(list_height)

        popup_width = max(self.width(), 260)
        popup_height = list_height + 12  # top+bottom outer margins
        popup.setFixedSize(popup_width, popup_height)

        # Qt.Popup windows are opaque by default, so rounded QSS corners
        # would otherwise show square window edges poking out — clip the
        # actual window shape to a rounded rect instead of relying on
        # WA_TranslucentBackground (whose offscreen compositing is flaky).
        radius = 16
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, popup_width, popup_height), radius, radius)
        popup.setMask(QRegion(path.toFillPolygon().toPolygon()))

        anchor = self.mapToGlobal(QPoint(0, self.height() + 6))
        popup.move(anchor)
        popup.show()
        if current_item is not None:
            listw.scrollToItem(current_item)

        self._popup = popup

    def _select(self, text: str):
        if self._popup is not None:
            self._popup.close()
        if text == self._value:
            return
        self.set_current_text(text)
        self.changed.emit(text)

    def _on_popup_destroyed(self):
        self._popup = None
