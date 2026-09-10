from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from . import backend


class DeviceScanWorker(QThread):
    """Runs the SoundVolumeView device scan off the GUI thread — spawning
    that process and waiting on its CSV output takes a few hundred ms,
    which would otherwise freeze the whole window every time Settings opens."""

    finished_scan = Signal(list)

    def run(self):
        self.finished_scan.emit(backend.list_output_devices())


class StatusScanWorker(QThread):
    """Counts the target app's processes and checks whether Voicemeeter runs.

    psutil walks every process on the machine for that, tens of ms each time —
    done here so neither the first status after launch nor the periodic
    refresh ever holds up a paint on the GUI thread."""

    finished_scan = Signal(int, bool)

    def __init__(self, target_process: str, voicemeeter_path: str):
        super().__init__()
        self._target = target_process
        self._voicemeeter_path = voicemeeter_path

    def run(self):
        running = backend.target_process_running(self._target) if self._target else 0
        vm_running = bool(backend.voicemeeter_pids(self._voicemeeter_path))
        self.finished_scan.emit(running, vm_running)
