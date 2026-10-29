from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from . import backend, icons, settings
from .device_picker import DevicePicker
from .overlay_base import ModalOverlay
from .scan_worker import DeviceScanWorker
from .toggle_switch import ToggleSwitch

_REFRESH_LABEL_IDLE = "  Actualiser les périphériques"
_REFRESH_LABEL_BUSY = "  Scan en cours…"


def _titled_row(icon_name: str, text: str, object_name: str, icon_size: int = 16) -> QHBoxLayout:
    """An accent line icon followed by its label."""
    row = QHBoxLayout()
    row.setSpacing(8)
    row.addWidget(icons.label(icon_name, "accent", icon_size))
    label = QLabel(text)
    label.setObjectName(object_name)
    row.addWidget(label)
    row.addStretch()
    return row


class SettingsOverlay(ModalOverlay):
    """In-window settings panel — the rest of the app dims/blurs behind it
    instead of opening a separate OS window. Lets the user pick which
    output each mode routes to, and whether Voicemeeter should be started
    and closed automatically."""

    def __init__(self, main_window):
        super().__init__(main_window)
        self._scan_worker: DeviceScanWorker | None = None

        card = QFrame()
        card.setObjectName("modalCard")
        card.setFixedWidth(380)
        root = QVBoxLayout(card)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(16)

        title_row = _titled_row("settings", "Paramètres", "cardTitle", icon_size=20)
        root.addLayout(title_row)

        subtitle = QLabel("Choisis la sortie audio utilisée par chaque mode.")
        subtitle.setObjectName("mutedText")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        self.live_picker = self._device_row(root, "live", "Sortie LIVE", main_window.live_device)
        self.normal_picker = self._device_row(root, "headphones", "Sortie NORMAL", main_window.normal_device)

        hint = QLabel("Liste basée sur les périphériques actifs détectés par SoundVolumeView.")
        hint.setObjectName("dimText")
        hint.setWordWrap(True)
        root.addWidget(hint)

        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        self.refresh_button = QPushButton(_REFRESH_LABEL_IDLE)
        self.refresh_button.setObjectName("pathButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        icons.bind(self.refresh_button, "refresh", "accent", 15)
        self.refresh_button.clicked.connect(self.refresh_devices)
        refresh_row.addWidget(self.refresh_button)
        root.addLayout(refresh_row)

        vm_row = QHBoxLayout()
        vm_box = QVBoxLayout()
        vm_box.setSpacing(2)
        vm_title = QLabel("Gérer Voicemeeter automatiquement")
        vm_title.setObjectName("sectionTitle")
        vm_title.setWordWrap(True)
        self.vm_sub = QLabel()
        self.vm_sub.setObjectName("mutedText")
        self.vm_sub.setStyleSheet("font-size: 11px;")
        self.vm_sub.setWordWrap(True)
        vm_box.addWidget(vm_title)
        vm_box.addWidget(self.vm_sub)
        vm_row.addLayout(vm_box, stretch=1)
        self._update_vm_subtitle()

        self.vm_path_button = QPushButton()
        self.vm_path_button.setObjectName("iconButton")
        self.vm_path_button.setFixedSize(30, 30)
        self.vm_path_button.setCursor(Qt.PointingHandCursor)
        self.vm_path_button.setToolTip("Choisir l'exécutable Voicemeeter")
        icons.bind(self.vm_path_button, "more", "muted", 20)
        self.vm_path_button.clicked.connect(self.choose_voicemeeter_path)
        vm_row.addWidget(self.vm_path_button)

        self.vm_switch = ToggleSwitch(icon_off="x", icon_on="check")
        self.vm_switch.setChecked(bool(main_window.manage_voicemeeter))
        self.vm_switch.toggled.connect(self.on_vm_toggled)
        vm_row.addWidget(self.vm_switch)
        root.addLayout(vm_row)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_button = QPushButton("Fermer")
        close_button.setObjectName("pathButton")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.close_overlay)
        close_row.addWidget(close_button)
        root.addLayout(close_row)

        self.set_card(card)
        self.refresh_devices()

    def _device_row(self, root: QVBoxLayout, icon_name: str, label_text: str, current_value: str) -> DevicePicker:
        box = QVBoxLayout()
        box.setSpacing(6)
        box.addLayout(_titled_row(icon_name, label_text, "sectionTitle"))

        picker = DevicePicker()
        picker.set_current_text(current_value)
        picker.changed.connect(self.on_devices_changed)
        box.addWidget(picker)
        root.addLayout(box)
        return picker

    def refresh_devices(self):
        if self._scan_worker is not None:
            return  # a scan is already running
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText(_REFRESH_LABEL_BUSY)

        worker = DeviceScanWorker()
        worker.finished_scan.connect(self._on_devices_scanned)
        self._scan_worker = worker
        worker.start()

    def _on_devices_scanned(self, devices: list[str]):
        self._scan_worker = None
        try:
            self.live_picker.set_items(devices)
            self.normal_picker.set_items(devices)
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText(_REFRESH_LABEL_IDLE)
        except RuntimeError:
            pass  # the panel was closed before the background scan finished

    def on_devices_changed(self, _text: str = ""):
        live = self.live_picker.current_text() or backend.DEFAULT_LIVE_DEVICE
        normal = self.normal_picker.current_text() or backend.DEFAULT_NORMAL_DEVICE
        self._main_window.live_device = live
        self._main_window.normal_device = normal
        self._main_window.app_settings["live_device"] = live
        self._main_window.app_settings["normal_device"] = normal
        settings.save_settings(self._main_window.app_settings)
        self._main_window.refresh_status()

    def on_vm_toggled(self, checked: bool):
        self._main_window.manage_voicemeeter = checked
        self._main_window.app_settings["manage_voicemeeter"] = checked
        settings.save_settings(self._main_window.app_settings)

    def choose_voicemeeter_path(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir l'exécutable Voicemeeter", "", "Exécutables (*.exe)"
        )
        if not path:
            return
        self._main_window.voicemeeter_path = path
        self._main_window.app_settings["voicemeeter_path"] = path
        settings.save_settings(self._main_window.app_settings)
        self._update_vm_subtitle()

    def _update_vm_subtitle(self):
        name = Path(self._main_window.voicemeeter_path).name
        self.vm_sub.setText(f"Lancé en LIVE, fermé en NORMAL  ·  {name}")
