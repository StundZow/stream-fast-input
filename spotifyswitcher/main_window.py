from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
)

from . import backend, icons, settings, theme
from .glass_background import GlassBackground
from .resources import ICON_PATH, resource_path
from .scan_worker import StatusScanWorker
from .settings_overlay import SettingsOverlay
from .style import build_stylesheet
from .toggle_switch import ToggleSwitch

REFRESH_MS = 2000
LOGO_SIZE = 32

# status badge kind -> (icon, colour role)
_BADGE_ICONS = {
    "success": ("check", "success"),
    "warning": ("alert", "warn"),
    "idle": ("info", "muted"),
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stream Fast Input")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.mode = settings.load_mode()
        self.app_settings = settings.load_settings()
        self.theme_name = self.app_settings.get("theme") or theme.detect_windows_theme()
        self.palette = theme.get_palette(self.theme_name)
        self.live_device = self.app_settings.get("live_device") or backend.DEFAULT_LIVE_DEVICE
        self.normal_device = self.app_settings.get("normal_device") or backend.DEFAULT_NORMAL_DEVICE
        self.manage_voicemeeter = bool(self.app_settings.get("manage_voicemeeter", True))
        self.target_process = self.app_settings.get("target_process") or backend.DEFAULT_TARGET_PROCESS
        self.voicemeeter_path = self.app_settings.get("voicemeeter_path") or backend.DEFAULT_VOICEMEETER_EXE

        icons.set_palette(self.palette)
        self._build_ui()
        self.apply_theme(self.theme_name)
        self.update_mode_buttons()

        if not backend.SVV.exists():
            self.show_status(
                f"Place SoundVolumeView.exe dans :\n{backend.SVV.parent}", "warning"
            )

        self.setFixedSize(452, 560)

        # Process scans run in a worker thread, so neither the first status after
        # launch nor the 2 s refresh ever makes the GUI thread wait on psutil.
        self._status_worker: StatusScanWorker | None = None
        self._first_status_seen = False
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_status)
        self._refresh_timer.start(REFRESH_MS)
        QTimer.singleShot(0, self.refresh_status)

    # ------------------------------------------------------------ UI ------
    def _build_ui(self):
        self.glass_background = GlassBackground()
        self.setCentralWidget(self.glass_background)
        root = QVBoxLayout(self.glass_background)
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(18)

        # header ------------------------------------------------------
        # explicit gaps instead of a layout-wide spacing: with the logo, the subtitle
        # only fits if the stretch doesn't also get padded on both sides
        header = QHBoxLayout()
        header.setSpacing(0)
        header.addWidget(self._logo_label())
        header.addSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("Stream Fast Input")
        title.setObjectName("title")
        subtitle = QLabel("Bascule la sortie audio d'une application")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("iconButton")
        self.settings_button.setFixedSize(34, 34)
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.setToolTip("Paramètres")
        icons.bind(self.settings_button, "settings", "muted", 19)
        self.settings_button.clicked.connect(self.open_settings)
        header.addWidget(self.settings_button)
        header.addSpacing(6)

        self.theme_switch = ToggleSwitch()
        self.theme_switch.setChecked(self.theme_name == "dark")
        self.theme_switch.toggled.connect(self.on_theme_toggled)
        header.addWidget(self.theme_switch)
        root.addLayout(header)

        # status card ---------------------------------------------------
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 16, 20, 16)
        status_layout.setSpacing(6)

        card_title_row = QHBoxLayout()
        card_title_row.setSpacing(8)
        card_title_row.addWidget(icons.label("volume", "accent", 18))
        self.app_title_label = QLabel()
        self.app_title_label.setObjectName("cardTitle")
        card_title_row.addWidget(self.app_title_label)
        card_title_row.addStretch()

        self.choose_app_button = QPushButton()
        self.choose_app_button.setObjectName("iconButton")
        self.choose_app_button.setFixedSize(30, 30)
        self.choose_app_button.setCursor(Qt.PointingHandCursor)
        self.choose_app_button.setToolTip("Choisir une autre application")
        icons.bind(self.choose_app_button, "more", "muted", 20)
        self.choose_app_button.clicked.connect(self.choose_target_app)
        card_title_row.addWidget(self.choose_app_button)
        status_layout.addLayout(card_title_row)
        self.update_app_title()

        self.device_label = QLabel("…")
        self.device_label.setObjectName("statusValue")
        self.device_label.setWordWrap(True)
        status_layout.addWidget(self.device_label)

        self.voicemeeter_label = QLabel("")
        self.voicemeeter_label.setObjectName("mutedText")
        status_layout.addWidget(self.voicemeeter_label)

        root.addWidget(status_card)

        # mode buttons ----------------------------------------------------
        mode_row = QHBoxLayout()
        mode_row.setSpacing(12)

        # The app icon's idea: the active output solid, the other one faded.
        self.btn_live = QPushButton("  LIVE")
        self.btn_normal = QPushButton("  NORMAL")
        for b, icon_name in ((self.btn_live, "live"), (self.btn_normal, "headphones")):
            b.setObjectName("modeButton")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(74)
            icons.bind(b, icon_name, "faded", 22, checked_role="white")
            mode_row.addWidget(b, stretch=1)

        self._mode_group = QButtonGroup(self)
        self._mode_group.setExclusive(True)
        self._mode_group.addButton(self.btn_live)
        self._mode_group.addButton(self.btn_normal)
        self.btn_live.clicked.connect(lambda: self.switch("LIVE"))
        self.btn_normal.clicked.connect(lambda: self.switch("NORMAL"))

        root.addLayout(mode_row)

        # status badge (result of the last switch) ------------------------
        self.status_badge = QFrame()
        self.status_badge.setObjectName("statusBadge")
        badge_layout = QHBoxLayout(self.status_badge)
        badge_layout.setContentsMargins(12, 10, 14, 10)
        badge_layout.setSpacing(9)
        self.status_badge_icon = QLabel()
        self.status_badge_icon.setFixedSize(16, 16)
        badge_layout.addWidget(self.status_badge_icon, alignment=Qt.AlignTop)
        self.status_badge_text = QLabel("")
        self.status_badge_text.setObjectName("statusBadgeText")
        self.status_badge_text.setWordWrap(True)
        badge_layout.addWidget(self.status_badge_text, stretch=1)
        root.addWidget(self.status_badge)
        self.show_status("En attente — choisissez LIVE ou NORMAL.", "idle")

        root.addStretch(1)

        # footer ------------------------------------------------------
        footer = QHBoxLayout()
        footer.addStretch()
        self.debug_button = QPushButton("Debug devices")
        self.debug_button.setObjectName("debugButton")
        self.debug_button.setCursor(Qt.PointingHandCursor)
        icons.bind(self.debug_button, "search", "dim", 13)
        self.debug_button.clicked.connect(self.dump_devices)
        footer.addWidget(self.debug_button)
        root.addLayout(footer)

    @staticmethod
    def _logo_label() -> QLabel:
        """The app icon itself, heading the window."""
        ratio = QApplication.instance().devicePixelRatio() if QApplication.instance() else 1.0
        side = round(LOGO_SIZE * ratio)
        logo = QPixmap(resource_path("assets/icon.png")).scaled(
            side, side, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo.setDevicePixelRatio(ratio)
        label = QLabel()
        label.setFixedSize(QSize(LOGO_SIZE, LOGO_SIZE))
        label.setPixmap(logo)
        return label

    # ------------------------------------------------------------ theme ---
    def apply_theme(self, name: str):
        self.theme_name = name
        self.palette = theme.get_palette(name)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(build_stylesheet(self.palette))
        icons.set_palette(self.palette)
        self.glass_background.set_theme(self.palette)

    def on_theme_toggled(self, checked: bool):
        name = "dark" if checked else "light"
        self.app_settings["theme"] = name
        settings.save_settings(self.app_settings)
        self.apply_theme(name)

    # ------------------------------------------------------------ status --
    def show_status(self, text: str, kind: str):
        icon_name, role = _BADGE_ICONS[kind]
        icons.bind_label(self.status_badge_icon, icon_name, role, 16)
        self.status_badge_text.setText(text)
        self.status_badge.setProperty("kind", kind)
        self.status_badge_text.setProperty("kind", kind)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.status_badge_text.style().unpolish(self.status_badge_text)
        self.status_badge_text.style().polish(self.status_badge_text)
        self.status_badge.setVisible(True)

    def dump_devices(self):
        out_dir = backend.dump_devices()
        os.startfile(out_dir)

    def open_settings(self):
        overlay = SettingsOverlay(self)
        overlay.open_over()

    def choose_target_app(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir l'application à router", "", "Exécutables (*.exe)"
        )
        if not path:
            return
        self.target_process = Path(path).name
        self.app_settings["target_process"] = self.target_process
        settings.save_settings(self.app_settings)
        self.update_app_title()
        self.refresh_status()

    def update_app_title(self):
        if self.target_process:
            self.app_title_label.setText(Path(self.target_process).stem)
        else:
            self.app_title_label.setText("Aucune application")

    # ------------------------------------------------------------ logic ---
    def device_for_mode(self, mode: str) -> str:
        return self.live_device if mode == "LIVE" else self.normal_device

    def switch(self, mode: str, silent: bool = False):
        if not self.target_process:
            self.show_status("Choisis d'abord une application avec le bouton ···.", "warning")
            return
        device = self.device_for_mode(mode)
        if not device:
            self.show_status(
                f"Configure la sortie {mode} dans les paramètres avant de basculer.",
                "warning",
            )
            return

        if self.manage_voicemeeter:
            vm_msg = (
                backend.start_voicemeeter(self.voicemeeter_path) if mode == "LIVE"
                else backend.stop_voicemeeter(self.voicemeeter_path)
            )
        else:
            vm_msg = "Voicemeeter non géré"

        ok, msg = backend.svv_set_app_default(device, self.target_process)
        if ok:
            self.mode = mode
            settings.save_mode(mode)
            self.update_mode_buttons()
            if not silent:
                self.show_status(f"{mode} → {device}  •  {vm_msg}", "success")
        else:
            self.show_status(msg, "warning")

        self.refresh_status()

    def update_mode_buttons(self):
        self.btn_live.setChecked(self.mode == "LIVE")
        self.btn_normal.setChecked(self.mode == "NORMAL")

    def refresh_status(self):
        if not self.target_process:
            self.device_label.setText("Choisis une application avec le bouton ···")
        if self._status_worker is not None:
            return  # a scan is already running
        worker = StatusScanWorker(self.target_process, self.voicemeeter_path)
        worker.finished_scan.connect(self._on_status_scanned)
        self._status_worker = worker
        worker.start()

    def _on_status_scanned(self, running: int, vm_running: bool):
        self._status_worker = None
        try:
            if self.target_process:
                if running == 0:
                    display_name = Path(self.target_process).stem
                    self.device_label.setText(f"{display_name} n'est pas lancé")
                else:
                    target = self.device_for_mode(self.mode)
                    self.device_label.setText(f"{running} processus → {target}  [{self.mode}]")
            self.voicemeeter_label.setText(
                "Voicemeeter : lancé" if vm_running else "Voicemeeter : fermé"
            )
        except RuntimeError:
            return  # the window was closed before the scan came back

        # Re-apply the remembered mode once, on the first status after launch —
        # only if the target app is actually running.
        if not self._first_status_seen:
            self._first_status_seen = True
            if running:
                self.switch(self.mode, silent=True)
