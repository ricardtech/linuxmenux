"""
Linux Menux Universal Package Manager
Thread-safe update checks, one-click execution, and reboot-required detection
across Debian/Ubuntu (APT), Arch/Manjaro (Pacman), RHEL/Rocky/Alma/Fedora (DNF), and openSUSE (Zypper).
"""

import os
import re
import shlex
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.distro import detect_system_info

UPDATE_LOCK_FILE = "/run/linuxmenux-update.lock"
_update_lock = threading.Lock()
_current_update_job: Dict[str, Any] = {
    "active": False,
    "started_at": 0,
    "status": "idle",
    "output_log": [],
    "returncode": None,
}


def is_update_in_progress() -> bool:
    """Check if an update is currently running."""
    return _current_update_job.get("active", False) or os.path.exists(UPDATE_LOCK_FILE)


def check_updates() -> Dict[str, Any]:
    """
    Check for pending system updates according to the active package manager.
    Returns status, package count, and package list.
    """
    sys_info = detect_system_info()
    mgr = sys_info["pkg_manager"]
    result: Dict[str, Any] = {
        "pkg_manager": mgr,
        "distro": sys_info["distro_name"],
        "pending_count": 0,
        "packages": [],
        "last_checked": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "error": None,
    }

    try:
        if mgr == "pacman":
            # Manjaro / Arch: checkupdates (part of pacman-contrib) or pacman -Qu
            cmd = ["checkupdates"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                lines = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
                result["pending_count"] = len(lines)
                for line in lines[:50]:
                    parts = line.split()
                    if len(parts) >= 4:
                        result["packages"].append({
                            "name": parts[0],
                            "old_version": parts[1],
                            "new_version": parts[3],
                        })
                    else:
                        result["packages"].append({"name": line, "old_version": "", "new_version": ""})
            elif proc.returncode == 2:
                # Code 2 on checkupdates means no updates available
                result["pending_count"] = 0
            else:
                # Fallback to pacman -Qu
                fb_proc = subprocess.run(["pacman", "-Qu"], capture_output=True, text=True, timeout=15)
                lines = [l.strip() for l in fb_proc.stdout.splitlines() if l.strip()]
                result["pending_count"] = len(lines)

        elif mgr == "apt":
            # Debian / Ubuntu: apt-get -s dist-upgrade
            proc = subprocess.run(["apt-get", "-s", "dist-upgrade"], capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                inst_lines = [l for l in proc.stdout.splitlines() if l.startswith("Inst ")]
                result["pending_count"] = len(inst_lines)
                for line in inst_lines[:50]:
                    m = re.match(r"Inst\s+([^\s]+)\s+\[([^\]]+)\]\s+\(([^)]+)\)", line)
                    if m:
                        result["packages"].append({
                            "name": m.group(1),
                            "old_version": m.group(2),
                            "new_version": m.group(3),
                        })

        elif mgr == "dnf":
            # RHEL / Rocky / Alma / Fedora: dnf check-update
            proc = subprocess.run(["dnf", "check-update", "-q"], capture_output=True, text=True, timeout=45)
            # DNF returns 100 if updates are available, 0 if no updates
            if proc.returncode in (0, 100):
                lines = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
                result["pending_count"] = len(lines)
                for line in lines[:50]:
                    parts = line.split()
                    if len(parts) >= 2:
                        result["packages"].append({"name": parts[0], "new_version": parts[1]})

        elif mgr == "zypper":
            # openSUSE: zypper --xmlout list-updates
            proc = subprocess.run(["zypper", "--non-interactive", "list-updates"], capture_output=True, text=True, timeout=45)
            lines = [l for l in proc.stdout.splitlines() if "v |" in l or " | " in l]
            # filter header
            pkgs = [l.strip() for l in lines if not l.startswith("S |") and not l.startswith("--")]
            result["pending_count"] = len(pkgs)

    except (subprocess.SubprocessError, OSError) as e:
        result["error"] = str(e)

    return result


def check_reboot_required() -> Dict[str, Any]:
    """
    Detect whether the host operating system requires a reboot.
    Supports Debian/Ubuntu marker files, RHEL needs-restarting, openSUSE zypper ps,
    and Arch/Manjaro running kernel vs disk modules comparison.
    """
    sys_info = detect_system_info()
    mgr = sys_info["pkg_manager"]
    running_kernel = sys_info["kernel"]

    result = {
        "reboot_required": False,
        "reason": None,
        "running_kernel": running_kernel,
        "installed_kernel": None,
    }

    # 1. Standard Debian/Ubuntu marker
    if os.path.exists("/run/reboot-required") or os.path.exists("/var/run/reboot-required"):
        result["reboot_required"] = True
        result["reason"] = "Debian/Ubuntu reboot-required marker exists"
        return result

    # 2. Arch Linux / Manjaro: Compare running kernel with /usr/lib/modules/
    if mgr == "pacman":
        modules_dir = Path("/usr/lib/modules")
        if modules_dir.exists():
            installed_kernels = [p.name for p in modules_dir.iterdir() if p.is_dir()]
            if installed_kernels and running_kernel not in installed_kernels:
                result["reboot_required"] = True
                result["reason"] = f"Running kernel ({running_kernel}) was updated/removed from /usr/lib/modules/"
                result["installed_kernel"] = installed_kernels[-1]
                return result

    # 3. RHEL / Rocky / Alma / Fedora: needs-restarting -r
    if mgr == "dnf":
        try:
            proc = subprocess.run(["needs-restarting", "-r"], capture_output=True, text=True, timeout=10)
            if proc.returncode == 1:
                result["reboot_required"] = True
                result["reason"] = "needs-restarting -r detected a reboot is required"
                return result
        except (subprocess.SubprocessError, OSError):
            pass

    # 4. openSUSE: zypper ps -s
    if mgr == "zypper":
        try:
            proc = subprocess.run(["zypper", "ps", "-s"], capture_output=True, text=True, timeout=10)
            if "reboot" in proc.stdout.lower() or proc.returncode == 1:
                result["reboot_required"] = True
                result["reason"] = "zypper ps detected kernel or system reboot required"
                return result
        except (subprocess.SubprocessError, OSError):
            pass

    return result


def apply_updates_async() -> Dict[str, Any]:
    """Trigger background package upgrade with safe locking."""
    global _current_update_job
    with _update_lock:
        if is_update_in_progress():
            return {"success": False, "message": "An update process is already running"}

        _current_update_job = {
            "active": True,
            "started_at": time.time(),
            "status": "running",
            "output_log": ["Starting package update process..."],
            "returncode": None,
        }

    thread = threading.Thread(target=_run_update_worker, daemon=True)
    thread.start()
    return {"success": True, "message": "Update initiated in background"}


def _run_update_worker():
    global _current_update_job
    sys_info = detect_system_info()
    mgr = sys_info["pkg_manager"]

    commands = []
    if mgr == "pacman":
        commands = [["pacman", "-Syu", "--noconfirm"]]
    elif mgr == "apt":
        commands = [
            ["apt-get", "update"],
            ["apt-get", "dist-upgrade", "-y", "-o", "Dpkg::Options::=--force-confdef", "-o", "Dpkg::Options::=--force-confold"]
        ]
    elif mgr == "dnf":
        commands = [["dnf", "upgrade", "-y"]]
    elif mgr == "zypper":
        commands = [["zypper", "--non-interactive", "update", "-y"]]

    try:
        Path(UPDATE_LOCK_FILE).touch()
        for cmd in commands:
            _current_update_job["output_log"].append(f"$ {' '.join(cmd)}")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                _current_update_job["output_log"].append(line.rstrip())
                if len(_current_update_job["output_log"]) > 1000:
                    _current_update_job["output_log"].pop(0)

            proc.wait()
            if proc.returncode != 0:
                _current_update_job["status"] = "failed"
                _current_update_job["returncode"] = proc.returncode
                _current_update_job["output_log"].append(f"Command failed with exit code {proc.returncode}")
                return

        _current_update_job["status"] = "completed"
        _current_update_job["returncode"] = 0
        _current_update_job["output_log"].append("Updates completed successfully.")

    except Exception as e:
        _current_update_job["status"] = "error"
        _current_update_job["output_log"].append(f"Exception during update: {str(e)}")
    finally:
        _current_update_job["active"] = False
        try:
            if os.path.exists(UPDATE_LOCK_FILE):
                os.remove(UPDATE_LOCK_FILE)
        except OSError:
            pass


def get_update_status() -> Dict[str, Any]:
    """Retrieve current update progress and logs."""
    return {
        "active": _current_update_job["active"],
        "status": _current_update_job["status"],
        "logs": _current_update_job["output_log"][-50:],
        "returncode": _current_update_job["returncode"],
    }


def execute_system_reboot() -> Dict[str, Any]:
    """Safely execute system reboot via systemctl reboot."""
    if is_update_in_progress():
        return {"success": False, "message": "Cannot reboot while an update is in progress."}

    def _do_reboot():
        time.sleep(1)
        subprocess.run(["systemctl", "reboot"], check=False)

    threading.Thread(target=_do_reboot, daemon=True).start()
    return {"success": True, "message": "System reboot initiated successfully."}
