from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from . import backend


class DeviceScanWorker(QThread):
    """Runs the SoundVolumeView device scan off the GUI thread — spawning
    that process and waiting on its CSV output takes a few hundred ms,
    which was previously freezing the whole window for that long every
    time Settings opened."""

    finished_scan = Signal(list)

    def run(self):
        self.finished_scan.emit(backend.list_output_devices())
