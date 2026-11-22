"""
Linux Menux System Metrics Collector
Gathers CPU, Memory, Disks, Network, and Sensor metrics safely using /proc and system utilities.
"""

import os
import platform
import subprocess
import time
from typing import Dict, Any, List


def get_cpu_info() -> Dict[str, Any]:
    """Retrieve load average and CPU usage."""
    load1, load5, load15 = os.getloadavg()
    cpu_count = os.cpu_count() or 1
    return {
        "cores": cpu_count,
        "load_1m": round(load1, 2),
        "load_5m": round(load5, 2),
        "load_15m": round(load15, 2),
        "load_percent": round((load1 / cpu_count) * 100, 1),
    }


def get_memory_info() -> Dict[str, Any]:
    """Read RAM and Swap usage from /proc/meminfo."""
    mem = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().split()[0]
                mem[key] = int(val) * 1024  # bytes

    total = mem.get("MemTotal", 0)
    avail = mem.get("MemAvailable", 0)
    used = total - avail
    pct = round((used / total * 100), 1) if total > 0 else 0.0

    swap_total = mem.get("SwapTotal", 0)
    swap_free = mem.get("SwapFree", 0)
    swap_used = swap_total - swap_free
    swap_pct = round((swap_used / swap_total * 100), 1) if swap_total > 0 else 0.0

    return {
        "ram_total": total,
        "ram_used": used,
        "ram_available": avail,
        "ram_percent": pct,
        "swap_total": swap_total,
        "swap_used": swap_used,
        "swap_percent": swap_pct,
    }


def get_disk_mounts() -> List[Dict[str, Any]]:
    """Inspect mounted filesystems with df."""
    mounts = []
    try:
        proc = subprocess.run(["df", "-B1", "-P", "-T"], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            lines = proc.stdout.splitlines()[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 7:
                    fs, fstype, total, used, avail, pct, target = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
                    if fs.startswith("/dev/") or fstype in ("zfs", "btrfs", "ext4", "xfs"):
                        mounts.append({
                            "device": fs,
                            "type": fstype,
                            "mountpoint": target,
                            "total_bytes": int(total),
                            "used_bytes": int(used),
                            "available_bytes": int(avail),
                            "usage_percent": pct.rstrip("%"),
                        })
    except (subprocess.SubprocessError, OSError):
        pass
    return mounts


def get_uptime_seconds() -> float:
    """Read system uptime in seconds from /proc/uptime."""
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.read().split()[0])
    except (OSError, IndexError):
        return 0.0


def collect_all_metrics() -> Dict[str, Any]:
    """Collect aggregate system health metrics."""
    return {
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disk_mounts(),
        "uptime_seconds": get_uptime_seconds(),
        "timestamp": time.time(),
    }
