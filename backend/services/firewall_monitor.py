"""
LinuxMenux Firewall Inspector
Safely queries Iptables, Nftables, and UFW without altering running configurations.
"""

import shutil
import subprocess
from typing import Dict, Any, List


def inspect_firewall() -> Dict[str, Any]:
    """Return summary of active firewall backend and rules."""
    result: Dict[str, Any] = {
        "active_backend": "none",
        "ufw_status": None,
        "docker_user_rules": [],
        "input_rules_count": 0,
        "forward_rules_count": 0,
    }

    # 1. Check UFW
    if shutil.which("ufw"):
        try:
            proc = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                result["active_backend"] = "ufw"
                result["ufw_status"] = proc.stdout.splitlines()[0] if proc.stdout else "unknown"
        except (subprocess.SubprocessError, OSError):
            pass

    # 2. Check iptables
    if shutil.which("iptables"):
        try:
            proc = subprocess.run(["iptables", "-L", "-n", "--line-numbers"], capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                if result["active_backend"] == "none":
                    result["active_backend"] = "iptables"

                lines = proc.stdout.splitlines()
                current_chain = None
                for line in lines:
                    line = line.strip()
                    if line.startswith("Chain "):
                        current_chain = line.split()[1]
                        continue
                    if not line or line.startswith("num") or line.startswith("Chain"):
                        continue

                    if current_chain == "DOCKER-USER":
                        result["docker_user_rules"].append(line)
                    elif current_chain == "INPUT":
                        result["input_rules_count"] += 1
                    elif current_chain == "FORWARD":
                        result["forward_rules_count"] += 1

        except (subprocess.SubprocessError, OSError):
            pass

    # 3. Check nftables if iptables not found
    if result["active_backend"] == "none" and shutil.which("nft"):
        result["active_backend"] = "nftables"

    return result
