"""
LinuxMenux Distro Detection Engine
Identifies Linux distribution family, package manager, and system capabilities.
"""

import os
import platform
import re
from typing import Dict, Any, Optional


def get_os_release() -> Dict[str, str]:
    """Parse /etc/os-release safely without shell execution."""
    data = {}
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def detect_system_info() -> Dict[str, Any]:
    """Return comprehensive system identification."""
    os_info = get_os_release()
    distro_id = os_info.get("ID", "").lower()
    id_like = [x.lower() for x in os_info.get("ID_LIKE", "").split()]
    name = os_info.get("PRETTY_NAME", os_info.get("NAME", platform.system()))
    version = os_info.get("VERSION_ID", os_info.get("VERSION", ""))
    kernel = platform.release()
    arch = platform.machine()
    hostname = platform.node()

    # Determine distribution family & package manager
    pkg_manager = "unknown"
    family = "unknown"

    if distro_id in ("debian", "ubuntu", "linuxmint", "pop", "kali", "raspbian") or any(x in id_like for x in ("debian", "ubuntu")):
        family = "debian"
        pkg_manager = "apt"
    elif distro_id in ("arch", "manjaro", "endeavouros", "garuda", "cachyos") or "arch" in id_like:
        family = "arch"
        pkg_manager = "pacman"
    elif distro_id in ("rhel", "centos", "rocky", "almalinux", "fedora", "oracle") or any(x in id_like for x in ("rhel", "fedora", "centos")):
        family = "rhel"
        pkg_manager = "dnf"
    elif distro_id in ("opensuse", "opensuse-leap", "opensuse-tumbleweed", "sles") or "suse" in id_like:
        family = "suse"
        pkg_manager = "zypper"

    return {
        "distro_id": distro_id,
        "distro_name": name,
        "distro_version": version,
        "distro_family": family,
        "pkg_manager": pkg_manager,
        "kernel": kernel,
        "architecture": arch,
        "hostname": hostname,
    }
