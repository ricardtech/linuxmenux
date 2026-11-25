"""
Persistent data directory resolver for Linux Menux.
Ensures metrics_history.db, settings, backups config, tokens, and auth state
survive both system reboots and installer upgrades.
"""

import os
import shutil


def get_persistent_data_dir() -> str:
    env_dir = os.environ.get("LINUXMENUX_DATA_DIR", "").strip()
    if env_dir:
        os.makedirs(env_dir, exist_ok=True)
        return env_dir

    legacy_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    system_dir = "/var/lib/linuxmenux"

    if os.geteuid() == 0 or (os.path.isdir(system_dir) and os.access(system_dir, os.W_OK)):
        os.makedirs(system_dir, exist_ok=True)
        # One-time non-destructive migration from legacy backend/data
        if os.path.isdir(legacy_dir):
            for fname in os.listdir(legacy_dir):
                src = os.path.join(legacy_dir, fname)
                dst = os.path.join(system_dir, fname)
                if os.path.isfile(src) and not os.path.exists(dst):
                    try:
                        shutil.copy2(src, dst)
                    except OSError:
                        pass
        return system_dir

    os.makedirs(legacy_dir, exist_ok=True)
    return legacy_dir
