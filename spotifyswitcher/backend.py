from __future__ import annotations

import sys
from pathlib import Path

from .settings import CONFIG_DIR

# psutil, subprocess and csv are imported inside the functions that use them: none of
# them is needed to draw the window, and together they cost ~150 ms at import — paid
# on the startup path if they sit up here.

# Shipped blank on purpose — every install has different hardware and apps,
# so there's nothing sensible to preselect. The UI prompts the user to
# configure each of these (target app, LIVE/NORMAL outputs) before use.
DEFAULT_LIVE_DEVICE = ""
DEFAULT_NORMAL_DEVICE = ""
DEFAULT_TARGET_PROCESS = ""

# The one default worth keeping: VB-Audio's own installer always puts
# Voicemeeter here, regardless of whose machine it's on.
DEFAULT_VOICEMEETER_EXE = r"C:\Program Files (x86)\VB\Voicemeeter\voicemeeter8x64.exe"

CREATE_NO_WINDOW = 0x08000000


def app_dir() -> Path:
    """Resolve the folder holding bundled resources (SoundVolumeView.exe).

    sys._MEIPASS is where PyInstaller actually puts bundled binaries in
    both onefile and onedir builds — onedir in particular nests everything
    under an `_internal` subfolder next to the exe, not beside the exe
    itself, so resolving via sys.executable's parent would miss it.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base)
    return Path(__file__).parent.parent


SVV = app_dir() / "SoundVolumeView.exe"


# ---------------------------------------------------------------------------
# SoundVolumeView wrappers
# ---------------------------------------------------------------------------
def svv_set_app_default(device_name: str, process_name: str) -> tuple[bool, str]:
    """Définit le device de sortie par défaut pour une app donnée.
    role: 0=Console, 1=Multimedia, 2=Communications — on applique aux trois.
    """
    import subprocess

    if not SVV.exists():
        return False, f"SoundVolumeView.exe introuvable dans {SVV.parent}"

    try:
        for role in ("0", "1", "2"):
            subprocess.run(
                [str(SVV), "/SetAppDefault", device_name, role, process_name],
                check=False,
                creationflags=CREATE_NO_WINDOW,
                timeout=5,
            )
        return True, f"Routé vers « {device_name} »"
    except Exception as e:
        return False, f"Erreur SoundVolumeView : {e}"


def svv_list_devices() -> str:
    """Dump la liste des devices via SoundVolumeView pour debug."""
    import subprocess

    if not SVV.exists():
        return "SoundVolumeView.exe introuvable."
    out_file = CONFIG_DIR / "svv_devices.txt"
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [str(SVV), "/scomma", str(out_file)],
            check=False,
            creationflags=CREATE_NO_WINDOW,
            timeout=10,
        )
        return out_file.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"Erreur : {e}"


def dump_devices() -> Path:
    svv_list_devices()
    return CONFIG_DIR


def list_output_devices() -> list[str]:
    """Scan currently active render (output) devices via SoundVolumeView, to
    populate the LIVE/NORMAL device pickers in Settings."""
    import csv
    import subprocess

    if not SVV.exists():
        return []
    out_file = CONFIG_DIR / "svv_devices.csv"
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [str(SVV), "/scomma", str(out_file)],
            check=False,
            creationflags=CREATE_NO_WINDOW,
            timeout=10,
        )
        names: set[str] = set()
        with out_file.open(encoding="utf-8-sig", errors="ignore", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("Type") == "Device" and row.get("Direction") == "Render":
                    name = row.get("Name")
                    if name:
                        names.add(name)
        return sorted(names, key=str.casefold)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Voicemeeter / target app detection
# ---------------------------------------------------------------------------
def _pids_named(process_name: str) -> list[int]:
    import psutil

    wanted = process_name.lower()
    return [p.pid for p in psutil.process_iter(["name"])
            if p.info["name"] and p.info["name"].lower() == wanted]


def voicemeeter_pids(voicemeeter_path: str) -> list[int]:
    return _pids_named(Path(voicemeeter_path).name)


def start_voicemeeter(voicemeeter_path: str) -> str:
    import subprocess

    if voicemeeter_pids(voicemeeter_path):
        return "Voicemeeter déjà lancé"
    if not Path(voicemeeter_path).exists():
        return f"Voicemeeter introuvable : {voicemeeter_path}"
    try:
        subprocess.Popen(
            [voicemeeter_path],
            creationflags=CREATE_NO_WINDOW,
            cwd=str(Path(voicemeeter_path).parent),
        )
        return "Voicemeeter lancé"
    except Exception as e:
        return f"Erreur au lancement de Voicemeeter : {e}"


def stop_voicemeeter(voicemeeter_path: str) -> str:
    import psutil

    pids = voicemeeter_pids(voicemeeter_path)
    if not pids:
        return "Voicemeeter pas en cours"
    killed = 0
    for pid in pids:
        try:
            p = psutil.Process(pid)
            p.terminate()
            try:
                p.wait(timeout=3)
            except psutil.TimeoutExpired:
                p.kill()
            killed += 1
        except Exception:
            pass
    return f"Voicemeeter fermé ({killed})"


def target_process_running(process_name: str) -> int:
    return len(_pids_named(process_name))
