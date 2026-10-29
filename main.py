import os
import subprocess
import sys
import time


def _mark(label: str):
    """Startup diagnostics, active only when SFI_TIMING names a log file: appends
    the time elapsed since the launch at each step of the startup sequence."""
    log_path = os.environ.get("SFI_TIMING")
    if not log_path:
        return
    import psutil

    proc = psutil.Process()
    root = proc
    # A onefile build runs the app in a child of the bootloader that extracted the
    # archive: count from that parent so the timeline starts at the double-click,
    # extraction included, and matches what an outside stopwatch sees.
    if getattr(sys, "frozen", False):
        parent = proc.parent()
        if parent is not None and parent.name().lower() == proc.name().lower():
            root = parent
    elapsed = time.time() - root.create_time()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{elapsed:7.3f}s  {label}\n")


class _Splash:
    """The launch screen runs in a second process (spotifyswitcher/splash.py): the app
    feeds it real progress over its stdin. If it's gone, the app just carries on."""

    def __init__(self):
        if getattr(sys, "frozen", False):
            command = [sys.executable, "--splash"]
        else:
            command = [sys.executable, os.path.abspath(__file__), "--splash"]
        try:
            self._proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError:
            self._proc = None

    def progress(self, percent: int):
        self._send(f"progress {percent}")

    def done(self):
        self._send("done")

    def _send(self, message: str):
        if self._proc is None or self._proc.stdin is None:
            return
        try:
            self._proc.stdin.write(f"{message}\n".encode("utf-8"))
            self._proc.stdin.flush()
        except (OSError, ValueError):
            self._proc = None


def main():
    if "--splash" in sys.argv:
        from spotifyswitcher.splash import run_splash

        sys.exit(run_splash())

    _mark("python_start")
    # Spawned before anything else, Qt included: every millisecond gained here is a
    # millisecond of blank screen less.
    splash = _Splash()
    _mark("splash_spawned")

    from PySide6.QtGui import QFontDatabase, QGuiApplication, QIcon
    from PySide6.QtWidgets import QApplication

    from spotifyswitcher.resources import ICON_PATH

    _mark("qt_imported")
    app = QApplication(sys.argv)
    _mark("qapp_created")
    splash.progress(10)
    app.setWindowIcon(QIcon(ICON_PATH))

    # The first text render of a process pays the Windows font database (~0.5 s with a
    # few hundred families installed) — once, but it freezes the thread. Triggering it
    # explicitly here lets the splash bar move on this real step instead of sitting
    # still. (The interface draws no emoji and no symbol Segoe UI lacks — icons are
    # SVG line drawings — so no fallback font is ever loaded on top of it.)
    QFontDatabase.families()
    _mark("fonts_ready")
    splash.progress(70)

    from spotifyswitcher.main_window import MainWindow

    _mark("main_window_imported")
    splash.progress(78)

    window = MainWindow()
    _mark("window_built")
    splash.progress(90)

    # Centered on the same point as the splash, so the hand-off doesn't jump.
    screen = QGuiApplication.primaryScreen()
    if screen:
        frame = window.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        window.move(frame.topLeft())

    window.show()
    app.processEvents()
    _mark("window_shown")
    splash.progress(100)
    splash.done()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
