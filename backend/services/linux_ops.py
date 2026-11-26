"""
Linux Menux Multi-Distro Operations Service
Provides real Storage/SMART, Hardware, Backup, Logs, Security (Firewall/Tailscale/Fail2Ban/Lynis),
Compliance Audit, Settings, and Linked Nodes across Debian/Ubuntu, Arch/Manjaro/BigLinux,
RHEL/Fedora/Rocky, and openSUSE.
"""

import json
import os
import re
import shutil
import secrets
import subprocess
import tarfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.distro import detect_system_info
from core.paths import get_persistent_data_dir
from services.host_inspector import (
    format_bytes,
    get_real_cpu_metrics,
    get_real_memory_metrics,
    get_real_network_info,
    get_real_storage_info,
    get_real_temperature,
)
from services.metrics_history import get_cached_updates

DATA_DIR = get_persistent_data_dir()
DEFAULT_BACKUP_DIR = "/var/backups/linuxmenux"


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_json(filename: str, default: Any) -> Any:
    _ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(filename: str, payload: Any) -> None:
    _ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _run_cmd(cmd: List[str], timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _install_packages_multi_distro(packages_by_mgr: Dict[str, List[str]]) -> Dict[str, Any]:
    info = detect_system_info()
    mgr = info.get("pkg_manager", "unknown")
    pkgs = packages_by_mgr.get(mgr, [])
    if not pkgs:
        return {"success": False, "message": f"Gerenciador '{mgr}' não suportado para instalação automática."}

    cmd_map = {
        "apt": ["apt-get", "install", "-y", *pkgs],
        "pacman": ["pacman", "-Sy", "--noconfirm", "--needed", *pkgs],
        "dnf": ["dnf", "install", "-y", *pkgs],
        "zypper": ["zypper", "--non-interactive", "install", *pkgs],
    }
    cmd = cmd_map.get(mgr)
    if not cmd:
        return {"success": False, "message": f"Comando indisponível para {mgr}"}

    try:
        if mgr == "apt":
            _run_cmd(["apt-get", "update", "-qq"], timeout=60)
        proc = _run_cmd(cmd, timeout=180)
        if proc.returncode == 0:
            return {"success": True, "message": f"Pacotes {', '.join(pkgs)} instalados com sucesso ({mgr})."}
        return {"success": False, "message": proc.stderr.strip() or proc.stdout.strip() or f"Erro {proc.returncode}"}
    except (subprocess.SubprocessError, OSError) as exc:
        return {"success": False, "message": str(exc)}


# ─── Storage & SMART ──────────────────────────────────────────────────────────

def _format_power_hours(hours: Optional[int]) -> str:
    if hours is None:
        return "N/D"
    days = hours // 24
    rem_h = hours % 24
    if days >= 30:
        months = days // 30
        rem_d = days % 30
        return f"{months}m {rem_d}d"
    if days > 0:
        return f"{days}d {rem_h}h"
    return f"{hours}h"


def _detect_root_disk() -> str:
    try:
        proc = _run_cmd(["findmnt", "-n", "-o", "SOURCE", "/"], timeout=3)
        src = proc.stdout.strip().split("[")[0]
        if src.startswith("/dev/"):
            return os.path.basename(src)
    except Exception:
        pass
    return ""


def get_physical_disks() -> Dict[str, Any]:
    smartctl_bin = shutil.which("smartctl")
    nvme_bin = shutil.which("nvme")
    root_dev = _detect_root_disk()
    disks: List[Dict[str, Any]] = []

    try:
        proc = _run_cmd(["lsblk", "-J", "-b", "-d", "-o", "NAME,KNAME,SIZE,TYPE,MODEL,SERIAL,ROTA,TRAN"], timeout=10)
        if proc.returncode == 0:
            parsed = json.loads(proc.stdout)
            for dev in parsed.get("blockdevices", []):
                if dev.get("type") != "disk":
                    continue
                name = dev.get("name", "")
                if name.startswith("loop") or name.startswith("ram") or name.startswith("zram"):
                    continue
                kname = f"/dev/{name}"
                size_b = int(dev.get("size") or 0)
                tran = (dev.get("tran") or ("nvme" if "nvme" in name else "sata")).upper()
                is_nvme = "nvme" in name.lower() or tran == "NVME"
                rota = dev.get("rota")
                media = "NVMe" if is_nvme else ("SSD" if rota in (False, 0, "0") else "HDD")
                is_system = bool(root_dev and (root_dev == name or root_dev.startswith(name)))

                smart_status = "DESCONHECIDO"
                temp_c: Optional[int] = None
                wear_pct: Optional[int] = None
                power_hours: Optional[int] = None
                power_cycles: Optional[int] = None
                crc_errors: int = 0
                data_written_bytes: int = 0
                controller: str = ""

                # Try reading PCI controller model from sysfs
                try:
                    uevent_p = Path(f"/sys/block/{name}/device/device/uevent")
                    if uevent_p.exists():
                        for uline in uevent_p.read_text(errors="ignore").splitlines():
                            if uline.startswith("DRIVER="):
                                controller = uline.split("=", 1)[1].strip()
                                break
                except OSError:
                    pass

                if smartctl_bin:
                    try:
                        sp = _run_cmd([smartctl_bin, "-j", "-H", "-A", kname], timeout=8)
                        if sp.stdout:
                            sdata = json.loads(sp.stdout)
                            passed = sdata.get("smart_status", {}).get("passed")
                            if passed is True:
                                smart_status = "APROVADO"
                            elif passed is False:
                                smart_status = "FALHA"
                            temp_c = sdata.get("temperature", {}).get("current")
                            power_hours = sdata.get("power_on_time", {}).get("hours")
                            power_cycles = sdata.get("power_cycle_count")
                            nvme_log = sdata.get("nvme_smart_health_information_log", {})
                            if "percentage_used" in nvme_log:
                                wear_pct = nvme_log["percentage_used"]
                            if "media_errors" in nvme_log:
                                crc_errors = int(nvme_log.get("media_errors") or 0)
                            if "data_units_written" in nvme_log:
                                data_written_bytes = int(nvme_log.get("data_units_written") or 0) * 512000
                            if not controller and sdata.get("model_family"):
                                controller = str(sdata.get("model_family"))
                            for attr in (sdata.get("ata_smart_attributes", {}).get("table") or []):
                                if attr.get("id") == 199:
                                    crc_errors = int(attr.get("raw", {}).get("value", 0) or 0)
                                elif attr.get("id") in (241, 246) and data_written_bytes == 0:
                                    data_written_bytes = int(attr.get("raw", {}).get("value", 0) or 0) * 512
                    except Exception:
                        pass

                disks.append({
                    "device": kname,
                    "name": name,
                    "model": (dev.get("model") or "Disco Linux").strip(),
                    "serial": (dev.get("serial") or "N/D").strip(),
                    "size_bytes": size_b,
                    "size_formatted": format_bytes(size_b),
                    "transport": tran,
                    "media_type": media,
                    "is_nvme": is_nvme,
                    "is_system": is_system,
                    "smart_status": smart_status,
                    "temperature": temp_c,
                    "wear_percent": wear_pct,
                    "power_on_hours": power_hours,
                    "power_on_formatted": _format_power_hours(power_hours),
                    "power_cycles": power_cycles,
                    "crc_errors": crc_errors,
                    "data_written_bytes": data_written_bytes,
                    "data_written_formatted": format_bytes(data_written_bytes) if data_written_bytes > 0 else "N/D",
                    "controller": controller or f"{tran} Storage Controller",
                })
    except Exception:
        pass

    return {
        "disks": disks,
        "smart_tools_installed": bool(smartctl_bin),
        "nvme_cli_installed": bool(nvme_bin),
        "history": _read_json("smart_history.json", []),
        "schedules": _read_json("smart_schedules.json", {"enabled": True, "items": []}),
    }


def get_disk_smart_detail(device: str) -> Dict[str, Any]:
    if not re.match(r"^/dev/[a-zA-Z0-9_-]+$", device):
        return {"error": "Dispositivo inválido", "installed": bool(shutil.which("smartctl"))}

    smartctl_bin = shutil.which("smartctl")
    if not smartctl_bin:
        return {"installed": False, "device": device, "attributes": [], "raw": ""}

    try:
        sp = _run_cmd([smartctl_bin, "-j", "-a", device], timeout=12)
        sdata = json.loads(sp.stdout) if sp.stdout else {}
        attrs: List[Dict[str, Any]] = []

        nvme_log = sdata.get("nvme_smart_health_information_log", {})
        if nvme_log:
            for k, v in nvme_log.items():
                attrs.append({"name": k.replace("_", " ").title(), "value": str(v), "status": "OK"})
        else:
            for row in sdata.get("ata_smart_attributes", {}).get("table", []):
                attrs.append({
                    "name": row.get("name", ""),
                    "value": str(row.get("raw", {}).get("string", row.get("value", ""))),
                    "status": "OK" if not row.get("when_failed") else "ALERTA",
                })

        raw_proc = _run_cmd([smartctl_bin, "-a", device], timeout=10)
        return {
            "installed": True,
            "device": device,
            "passed": sdata.get("smart_status", {}).get("passed"),
            "temperature": sdata.get("temperature", {}).get("current"),
            "power_on_hours": sdata.get("power_on_time", {}).get("hours"),
            "power_cycles": sdata.get("power_cycle_count"),
            "attributes": attrs,
            "raw": raw_proc.stdout[:12000],
        }
    except Exception as exc:
        return {"installed": True, "device": device, "error": str(exc), "attributes": [], "raw": ""}


def install_smart_tools() -> Dict[str, Any]:
    return _install_packages_multi_distro({
        "apt": ["smartmontools", "nvme-cli"],
        "pacman": ["smartmontools", "nvme-cli"],
        "dnf": ["smartmontools", "nvme-cli"],
        "zypper": ["smartmontools", "nvme-cli"],
    })


def run_smart_test(device: str, mode: str = "short") -> Dict[str, Any]:
    if not re.match(r"^/dev/[a-zA-Z0-9_-]+$", device):
        return {"success": False, "message": "Dispositivo inválido"}
    smartctl_bin = shutil.which("smartctl")
    if not smartctl_bin:
        return {"success": False, "message": "smartmontools não instalado"}
    test_type = "long" if mode == "extended" else "short"
    try:
        proc = _run_cmd([smartctl_bin, "-t", test_type, device], timeout=15)
        history = _read_json("smart_history.json", [])
        history.insert(0, {
            "device": device,
            "mode": "Estendido" if test_type == "long" else "Curto",
            "status": "Iniciado" if proc.returncode == 0 else "Erro",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output": (proc.stdout or proc.stderr).strip()[:300],
        })
        _write_json("smart_history.json", history[:50])
        return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def add_firewall_rule(port: str, proto: str = "tcp", action: str = "allow") -> Dict[str, Any]:
    """Add a firewall rule safely across UFW, firewalld, or iptables."""
    if not re.match(r"^\d{1,5}$", str(port)) or not (1 <= int(port) <= 65535):
        return {"success": False, "message": "Porta inválida (1-65535)"}
    proto = "udp" if proto == "udp" else "tcp"
    action = "deny" if action == "deny" else "allow"

    try:
        if shutil.which("ufw"):
            proc = _run_cmd(["ufw", action, f"{port}/{proto}"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("firewall-cmd"):
            op = "--add-port" if action == "allow" else "--remove-port"
            proc = _run_cmd(["firewall-cmd", "--permanent", op, f"{port}/{proto}"], timeout=10)
            _run_cmd(["firewall-cmd", "--reload"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("iptables"):
            target = "ACCEPT" if action == "allow" else "DROP"
            proc = _run_cmd(["iptables", "-A", "INPUT", "-p", proto, "--dport", str(port), "-j", target], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip() or "Regra aplicada"}
        return {"success": False, "message": "Nenhum firewall (UFW, firewalld, iptables) encontrado"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def toggle_firewall_engine(enable: bool) -> Dict[str, Any]:
    """Ativa ou desativa o firewall detectado no host (UFW ou firewalld)."""
    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" or ("ufw" in info.get("installed_engines", []) and engine_id in ("none", "iptables")):
        ufw_bin = shutil.which("ufw")
        if ufw_bin:
            cmd = [ufw_bin, "--force", "enable"] if enable else [ufw_bin, "disable"]
            proc = _run_cmd(cmd, timeout=15)
            return {"success": proc.returncode == 0, "engine": "UFW", "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" or "firewalld" in info.get("installed_engines", []):
        action = "start" if enable else "stop"
        proc = _run_cmd(["systemctl", action, "firewalld"], timeout=15)
        return {"success": proc.returncode == 0, "engine": "firewalld", "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": "Nenhum gerenciador com ativação automática (UFW ou firewalld) encontrado neste host."}


def delete_firewall_rule(rule_ref: str) -> Dict[str, Any]:
    """Remove uma regra do firewall ativo (UFW, firewalld ou iptables)."""
    rule_ref = str(rule_ref or "").strip()
    if not rule_ref:
        return {"success": False, "error": "Identificador da regra inválido."}

    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" and shutil.which("ufw"):
        if not rule_ref.isdigit():
            return {"success": False, "error": "Número de regra UFW inválido."}
        proc = _run_cmd(["ufw", "--force", "delete", rule_ref], timeout=15)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" and shutil.which("firewall-cmd"):
        if rule_ref.startswith("svc:"):
            svc = rule_ref[4:]
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-service={svc}"], timeout=10)
        else:
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-port={rule_ref}"], timeout=10)
        _run_cmd(["firewall-cmd", "--reload"], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "iptables" and shutil.which("iptables") and rule_ref.isdigit():
        proc = _run_cmd(["iptables", "-D", "INPUT", rule_ref], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": f"Remoção não suportada ou motor '{engine_id}' indisponível."}


def get_backup_file_path(filename: str) -> Optional[str]:
    if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", filename):
        return None
    target = os.path.join(_get_backup_dir(), filename)
    return target if os.path.exists(target) else None

def restore_backup(source: str, target_name: str) -> Dict[str, Any]:
    """Safely restore a local or Cloudflare R2 .tar.gz backup into a recovery folder."""
    bdir = _get_backup_dir()
    local_file: Optional[str] = None
    if source == "r2":
        cfg = _resolve_r2_cfg()
        if not all([cfg["endpoint"], cfg["bucket"], cfg["access_key"], cfg["secret_key"]]):
            return {"success": False, "message": "Cloudflare R2 não configurado"}
        try:
            raw = _s3_signed_request("GET", cfg["endpoint"], cfg["bucket"], target_name, cfg["access_key"], cfg["secret_key"])
            fname = os.path.basename(target_name)
            if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", fname):
                return {"success": False, "message": "Nome de arquivo inválido"}
            local_file = os.path.join(bdir, fname)
            Path(local_file).write_bytes(raw)
        except Exception as exc:
            return {"success": False, "message": f"Erro ao baixar do R2: {exc}"}
    else:
        local_file = get_backup_file_path(target_name)
        if not local_file:
            return {"success": False, "message": "Backup local não encontrado"}

    restore_dir = os.path.join(bdir, "restored", datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(restore_dir, exist_ok=True)
    try:
        with tarfile.open(local_file, "r:gz") as tar:
            for member in tar.getmembers():
                member_path = os.path.abspath(os.path.join(restore_dir, member.name))
                if not member_path.startswith(os.path.abspath(restore_dir) + os.sep) and member_path != os.path.abspath(restore_dir):
                    return {"success": False, "message": f"Caminho inválido bloqueado no arquivo: {member.name}"}
            tar.extractall(path=restore_dir)
        return {"success": True, "restored_to": restore_dir, "message": f"Backup restaurado em {restore_dir}"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def delete_backup_file(filename: str) -> Dict[str, Any]:
    if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", filename):
        return {"success": False, "message": "Nome de arquivo inválido"}
    bdir = _get_backup_dir()
    target = os.path.join(bdir, filename)
    if os.path.exists(target):
        os.remove(target)
        return {"success": True}
    return {"success": False, "message": "Arquivo não encontrado"}


# ─── System Logs (journalctl / syslog) ────────────────────────────────────────

def get_system_logs(
    search: str = "",
    level: str = "all",
    since: str = "24h",
    unit: str = "all",
    limit: int = 100,
) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    units_set = set()
    journal_bin = shutil.which("journalctl")
    since_map = {"1h": "1 hour ago", "24h": "1 day ago", "7d": "7 days ago", "all": None}
    since_arg = since_map.get(since, "1 day ago")

    if journal_bin:
        cmd = [journal_bin, "-n", str(min(limit, 300)), "--no-pager", "-o", "json"]
        if since_arg:
            cmd.extend(["--since", since_arg])
        if level == "error":
            cmd.extend(["-p", "err"])
        elif level == "warning":
            cmd.extend(["-p", "warning"])
        if unit and unit != "all" and re.match(r"^[a-zA-Z0-9_.:@-]+$", unit):
            cmd.extend(["-u", unit])
        try:
            proc = _run_cmd(cmd, timeout=8)
            for line in proc.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    msg = str(row.get("MESSAGE", ""))
                    u = row.get("_SYSTEMD_UNIT") or row.get("SYSLOG_IDENTIFIER") or "system"
                    units_set.add(u)
                    prio = int(row.get("PRIORITY", 6))
                    lvl = "Erro" if prio <= 3 else ("Aviso" if prio == 4 else "Info")
                    ts_us = int(row.get("__REALTIME_TIMESTAMP", 0))
                    ts_str = datetime.fromtimestamp(ts_us / 1_000_000).strftime("%Y-%m-%d %H:%M:%S") if ts_us else ""
                    if search and search.lower() not in msg.lower() and search.lower() not in u.lower():
                        continue
                    entries.append({
                        "timestamp": ts_str,
                        "unit": u,
                        "level": lvl,
                        "pid": row.get("_PID", "-"),
                        "message": msg,
                    })
                except Exception:
                    continue
        except Exception:
            pass

    entries.reverse()
    errors = sum(1 for e in entries if e["level"] == "Erro")
    warnings = sum(1 for e in entries if e["level"] == "Aviso")
    bk = get_backup_overview()
    bk_files = bk.get("backups", [])
    bk_bytes = sum(int(x.get("size_bytes", 0)) for x in bk_files)
    return {
        "entries": entries,
        "total": len(entries),
        "errors": errors,
        "warnings": warnings,
        "services": sorted(units_set),
        "backups_count": len(bk_files),
        "backups_size_formatted": format_bytes(bk_bytes) if bk_bytes > 0 else "0 B",
    }


# ─── Security (Firewall, Tailscale, Fail2Ban, Lynis, API Tokens) ──────────────

def _inspect_firewall_smart() -> Dict[str, Any]:
    """Detecta de forma inteligente UFW, firewalld, nftables e iptables, estado ativo e regras estruturadas."""
    installed_engines: List[str] = []
    if shutil.which("ufw"):
        installed_engines.append("ufw")
    if shutil.which("firewall-cmd"):
        installed_engines.append("firewalld")
    if shutil.which("nft"):
        installed_engines.append("nftables")
    if shutil.which("iptables"):
        installed_engines.append("iptables")

    fw_engine = "Nenhum"
    fw_engine_id = "none"
    fw_active = False
    default_policy = ""
    fw_rules: List[str] = []
    parsed_rules: List[Dict[str, Any]] = []

    # 1. Verifica UFW (preferido quando ativo ou quando instalado no host)
    if "ufw" in installed_engines:
        p = _run_cmd(["ufw", "status", "verbose"], timeout=5)
        if p.returncode == 0:
            out = p.stdout or ""
            is_ufw_active = "Status: active" in out
            if is_ufw_active:
                fw_engine = "UFW"
                fw_engine_id = "ufw"
                fw_active = True
                for line in out.splitlines():
                    if line.lower().startswith("default:"):
                        default_policy = line.split(":", 1)[1].strip()
                        break
                pn = _run_cmd(["ufw", "status", "numbered"], timeout=5)
                if pn.returncode == 0:
                    for line in pn.stdout.splitlines():
                        m = re.match(r"^\[\s*(\d+)\]\s+(.+?)\s+(ALLOW IN|DENY IN|REJECT IN|LIMIT IN|ALLOW OUT|DENY OUT|ALLOW|DENY|REJECT|LIMIT)\s+(.+)$", line.strip())
                        if m:
                            num = int(m.group(1))
                            target = m.group(2).strip()
                            action_raw = m.group(3).strip()
                            from_ip = m.group(4).strip()
                            action_norm = "deny" if ("DENY" in action_raw or "REJECT" in action_raw) else "allow"
                            fw_rules.append(line.strip())
                            parsed_rules.append({
                                "number": str(num),
                                "target": target,
                                "action": action_norm,
                                "action_label": action_raw,
                                "from_ip": from_ip,
                                "raw": line.strip(),
                            })

    # 2. Verifica firewalld se nenhum motor ativo foi encontrado ainda
    if not fw_active and "firewalld" in installed_engines:
        p = _run_cmd(["firewall-cmd", "--state"], timeout=5)
        if p.returncode == 0 and "running" in (p.stdout or "").lower():
            fw_engine = "firewalld"
            fw_engine_id = "firewalld"
            fw_active = True
            lp = _run_cmd(["firewall-cmd", "--list-all"], timeout=5)
            if lp.returncode == 0:
                zone_ports: List[str] = []
                zone_services: List[str] = []
                for line in lp.stdout.splitlines():
                    s = line.strip()
                    if s.startswith("target:"):
                        default_policy = s.split(":", 1)[1].strip()
                    elif s.startswith("ports:"):
                        zone_ports = [x for x in s.split(":", 1)[1].strip().split() if x]
                    elif s.startswith("services:"):
                        zone_services = [x for x in s.split(":", 1)[1].strip().split() if x]
                for pt in zone_ports:
                    raw = f"{pt} ALLOW IN (firewalld)"
                    fw_rules.append(raw)
                    parsed_rules.append({
                        "number": pt,
                        "target": pt,
                        "action": "allow",
                        "action_label": "ALLOW IN",
                        "from_ip": "zone",
                        "raw": raw,
                    })
                for svc in zone_services:
                    raw = f"service:{svc} ALLOW IN (firewalld)"
                    fw_rules.append(raw)
                    parsed_rules.append({
                        "number": f"svc:{svc}",
                        "target": svc,
                        "action": "allow",
                        "action_label": "SERVICE",
                        "from_ip": "zone",
                        "raw": raw,
                    })

    # 3. Verifica nftables se ainda inativo
    if not fw_active and "nftables" in installed_engines:
        svc = _run_cmd(["systemctl", "is-active", "nftables"], timeout=4)
        if svc.returncode == 0 and svc.stdout.strip() == "active":
            fw_engine = "nftables"
            fw_engine_id = "nftables"
            fw_active = True
            np = _run_cmd(["nft", "list", "ruleset"], timeout=5)
            if np.returncode == 0:
                for line in np.stdout.splitlines():
                    s = line.strip()
                    if "dport" in s or "policy" in s:
                        if "policy " in s and not default_policy:
                            default_policy = s
                        elif "dport" in s:
                            action_norm = "deny" if ("drop" in s or "reject" in s) else "allow"
                            fw_rules.append(s)
                            parsed_rules.append({
                                "number": str(len(parsed_rules) + 1),
                                "target": s,
                                "action": action_norm,
                                "action_label": "DROP" if action_norm == "deny" else "ACCEPT",
                                "from_ip": "Anywhere",
                                "raw": s,
                            })

    # 4. Verifica iptables se nenhum dos gerenciadores acima está ativo
    if not fw_active and "iptables" in installed_engines:
        p = _run_cmd(["iptables", "-L", "INPUT", "-n", "--line-numbers"], timeout=5)
        if p.returncode == 0:
            raw_lines = p.stdout.splitlines()
            if raw_lines and "policy " in raw_lines[0]:
                m_pol = re.search(r"policy\s+(\w+)", raw_lines[0])
                if m_pol:
                    default_policy = m_pol.group(1)
            for line in raw_lines[2:]:
                s = line.strip()
                if not s:
                    continue
                parts = s.split()
                if len(parts) >= 5 and parts[0].isdigit():
                    num = parts[0]
                    target_act = parts[1]
                    proto = parts[2]
                    src = parts[4]
                    dport_m = re.search(r"dpt:(\d+)", s)
                    target_label = f"{dport_m.group(1)}/{proto}" if dport_m else f"{proto} ({src})"
                    action_norm = "deny" if target_act in ("DROP", "REJECT") else "allow"
                    fw_rules.append(s)
                    parsed_rules.append({
                        "number": num,
                        "target": target_label,
                        "action": action_norm,
                        "action_label": target_act,
                        "from_ip": src,
                        "raw": s,
                    })
            if parsed_rules:
                fw_engine = "iptables"
                fw_engine_id = "iptables"
                fw_active = True

    # 5. Se nenhum motor está ativo, identifica o melhor motor instalado pronto para uso
    if not fw_active and fw_engine_id == "none":
        if "ufw" in installed_engines:
            fw_engine = "UFW"
            fw_engine_id = "ufw"
        elif "firewalld" in installed_engines:
            fw_engine = "firewalld"
            fw_engine_id = "firewalld"
        elif "iptables" in installed_engines:
            fw_engine = "iptables"
            fw_engine_id = "iptables"
        elif "nftables" in installed_engines:
            fw_engine = "nftables"
            fw_engine_id = "nftables"

    rules_joined = " ".join(fw_rules).lower()
    has_port_8008 = bool(re.search(r"(?:^|\D)8008(?:/tcp|\b)", rules_joined))
    has_port_22 = bool(re.search(r"(?:^|\D)22(?:/tcp|\b)|ssh", rules_joined))

    return {
        "engine": fw_engine,
        "engine_id": fw_engine_id,
        "installed_engines": installed_engines,
        "active": fw_active,
        "default_policy": default_policy,
        "rules": fw_rules[:50],
        "parsed_rules": parsed_rules[:50],
        "has_port_8008": has_port_8008,
        "has_port_22": has_port_22,
    }


def get_security_overview() -> Dict[str, Any]:
    # Firewall multi-distro inteligente: UFW, firewalld, nftables, iptables
    fw_info = _inspect_firewall_smart()

    # Tailscale
    ts_bin = shutil.which("tailscale")
    ts_installed = bool(ts_bin)
    ts_running = False
    ts_ip = ""
    if ts_bin:
        tp = _run_cmd([ts_bin, "ip", "-4"], timeout=4)
        if tp.returncode == 0 and tp.stdout.strip():
            ts_running = True
            ts_ip = tp.stdout.strip().splitlines()[0]

    # Fail2Ban
    f2b_bin = shutil.which("fail2ban-client")
    f2b_installed = bool(f2b_bin)
    f2b_running = False
    f2b_version = ""
    f2b_jails: List[str] = []
    f2b_jail_details: List[Dict[str, Any]] = []
    f2b_currently_banned = 0
    f2b_total_banned = 0
    f2b_total_failed = 0
    if f2b_bin:
        vp = _run_cmd([f2b_bin, "--version"], timeout=4)
        if vp.returncode == 0 and vp.stdout.strip():
            vm = re.search(r"(\d+\.\d+\.\d+)", vp.stdout)
            f2b_version = f"v{vm.group(1)}" if vm else vp.stdout.strip().splitlines()[0]
        fp = _run_cmd([f2b_bin, "status"], timeout=5)
        if fp.returncode == 0:
            f2b_running = True
            m = re.search(r"Jail list:\s*(.+)", fp.stdout)
            if m:
                f2b_jails = [j.strip() for j in m.group(1).split(",") if j.strip()]
            jail_meta = {
                "sshd": ("SSH", "Bloqueia falhas repetidas de login SSH."),
                "linuxmenux": ("Linux Menux Monitor", "Bloqueia falhas repetidas de login do Monitor."),
                "nginx-http-auth": ("Nginx Auth", "Bloqueia falhas repetidas de autenticação HTTP."),
                "caddy": ("Caddy Proxy", "Protege endpoints atrás do proxy reverso."),
            }
            for jname in f2b_jails:
                jp = _run_cmd([f2b_bin, "status", jname], timeout=5)
                cur_b = 0
                tot_b = 0
                cur_f = 0
                tot_f = 0
                ips: List[str] = []
                if jp.returncode == 0:
                    mc = re.search(r"Currently banned:\s*(\d+)", jp.stdout)
                    mt = re.search(r"Total banned:\s*(\d+)", jp.stdout)
                    mcf = re.search(r"Currently failed:\s*(\d+)", jp.stdout)
                    mtf = re.search(r"Total failed:\s*(\d+)", jp.stdout)
                    mi = re.search(r"Banned IP list:\s*(.+)", jp.stdout)
                    if mc:
                        cur_b = int(mc.group(1))
                    if mt:
                        tot_b = int(mt.group(1))
                    if mcf:
                        cur_f = int(mcf.group(1))
                    if mtf:
                        tot_f = int(mtf.group(1))
                    if mi:
                        ips = [x.strip() for x in mi.group(1).split() if x.strip()]

                def _get_f2b_val(key: str, default: str) -> str:
                    rp = _run_cmd([f2b_bin, "get", jname, key], timeout=3)
                    return rp.stdout.strip().splitlines()[-1] if rp.returncode == 0 and rp.stdout.strip() else default

                maxretry = _get_f2b_val("maxretry", "3")
                bantime_raw = _get_f2b_val("bantime", "3600")
                findtime_raw = _get_f2b_val("findtime", "600")

                def _fmt_duration(val: str) -> str:
                    try:
                        sec = int(val)
                        if sec >= 3600 and sec % 3600 == 0:
                            return f"{sec // 3600}h"
                        if sec >= 60 and sec % 60 == 0:
                            return f"{sec // 60}m"
                        return f"{sec}s"
                    except Exception:
                        return val

                label, desc = jail_meta.get(jname, (jname.upper(), f"Proteção automática para o serviço {jname}."))
                f2b_currently_banned += cur_b
                f2b_total_banned += tot_b
                f2b_total_failed += tot_f
                f2b_jail_details.append({
                    "name": jname,
                    "label": label,
                    "description": desc,
                    "currently_banned": cur_b,
                    "total_banned": tot_b,
                    "currently_failed": cur_f,
                    "total_failed": tot_f,
                    "banned_ips": ips,
                    "maxretry": maxretry,
                    "bantime": _fmt_duration(bantime_raw),
                    "findtime": _fmt_duration(findtime_raw),
                })

    # Lynis
    lynis_bin = shutil.which("lynis")
    lynis_installed = bool(lynis_bin)
    lynis_reports = _read_json("lynis_reports.json", [])

    # API Tokens
    tokens = _read_json("api_tokens.json", [])

    return {
        "firewall": fw_info,
        "tailscale": {"installed": ts_installed, "running": ts_running, "ip": ts_ip},
        "fail2ban": {
            "installed": f2b_installed,
            "running": f2b_running,
            "version": f2b_version,
            "jails": f2b_jails,
            "jail_details": f2b_jail_details,
            "currently_banned": f2b_currently_banned,
            "total_banned": f2b_total_banned,
            "total_failed": f2b_total_failed,
        },
        "lynis": {"installed": lynis_installed, "reports": lynis_reports},
        "api_tokens": tokens,
    }


def _configure_fail2ban_defaults() -> Dict[str, Any]:
    """Cria filtro do Linux Menux e jail.local com sshd + linuxmenux e whitelist."""
    try:
        os.makedirs("/etc/fail2ban/filter.d", exist_ok=True)
        auth_log = "/var/log/linuxmenux-auth.log"
        if not os.path.exists(auth_log):
            with open(auth_log, "a", encoding="utf-8"):
                pass

        filter_conf = (
            "[Definition]\n"
            "failregex = ^.*linuxmenux-auth: Failed login from <HOST>.*$\n"
            "ignoreregex =\n"
        )
        with open("/etc/fail2ban/filter.d/linuxmenux.conf", "w", encoding="utf-8") as fh:
            fh.write(filter_conf)

        settings = get_settings()
        trusted = list(settings.get("fail2ban_trusted_ips") or [])
        base_ignore = ["127.0.0.1/8", "::1"]
        for ip in trusted:
            if ip and ip not in base_ignore:
                base_ignore.append(ip)

        jail_local = (
            "[DEFAULT]\n"
            f"ignoreip = {' '.join(base_ignore)}\n"
            "bantime = 1h\n"
            "findtime = 10m\n"
            "maxretry = 3\n\n"
            "[sshd]\n"
            "enabled = true\n"
            "port = ssh\n"
            "backend = systemd\n"
            "maxretry = 3\n"
            "findtime = 10m\n"
            "bantime = 1h\n\n"
            "[linuxmenux]\n"
            "enabled = true\n"
            "port = 8008,80,443\n"
            "filter = linuxmenux\n"
            f"logpath = {auth_log}\n"
            "maxretry = 3\n"
            "findtime = 10m\n"
            "bantime = 1h\n"
        )
        with open("/etc/fail2ban/jail.local", "w", encoding="utf-8") as fh:
            fh.write(jail_local)

        _run_cmd(["systemctl", "enable", "--now", "fail2ban"], timeout=15)
        _run_cmd(["systemctl", "restart", "fail2ban"], timeout=15)
        return {"configured": True}
    except Exception as exc:
        return {"configured": False, "error": str(exc)}


def install_security_tool(tool: str) -> Dict[str, Any]:
    if tool == "fail2ban":
        res = _install_packages_multi_distro({
            "apt": ["fail2ban"],
            "pacman": ["fail2ban"],
            "dnf": ["fail2ban"],
            "zypper": ["fail2ban"],
        })
        if res.get("success"):
            cfg_res = _configure_fail2ban_defaults()
            if cfg_res.get("configured"):
                res["message"] = (res.get("message") or "") + " Jails sshd e linuxmenux configurados com sucesso."
            elif cfg_res.get("error"):
                res["message"] = (res.get("message") or "") + f" (Aviso na configuração: {cfg_res['error']})"
        return res
    if tool == "lynis":
        return _install_packages_multi_distro({
            "apt": ["lynis"],
            "pacman": ["lynis"],
            "dnf": ["lynis"],
            "zypper": ["lynis"],
        })
    return {"success": False, "message": "Ferramenta desconhecida"}


def run_lynis_audit() -> Dict[str, Any]:
    lynis_bin = shutil.which("lynis")
    if not lynis_bin:
        return {"success": False, "message": "Lynis não está instalado."}
    try:
        proc = _run_cmd([lynis_bin, "audit", "system", "--quick", "--no-colors"], timeout=120)
        hardening = "-"
        warnings = 0
        suggestions = 0
        m = re.search(r"Hardening index\s*:\s*(\d+)", proc.stdout)
        if m:
            hardening = m.group(1)
        mw = re.search(r"Warnings\s*\((\d+)\)", proc.stdout)
        if mw:
            warnings = int(mw.group(1))
        ms = re.search(r"Suggestions\s*\((\d+)\)", proc.stdout)
        if ms:
            suggestions = int(ms.group(1))

        reports = _read_json("lynis_reports.json", [])
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "hardening_index": hardening,
            "warnings": warnings,
            "suggestions": suggestions,
        }
        reports.insert(0, report)
        _write_json("lynis_reports.json", reports[:20])
        return {"success": True, "report": report}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def add_firewall_rule(port: str, proto: str = "tcp", action: str = "allow") -> Dict[str, Any]:
    """Add a firewall rule safely across UFW, firewalld, or iptables."""
    if not re.match(r"^\d{1,5}$", str(port)) or not (1 <= int(port) <= 65535):
        return {"success": False, "message": "Porta inválida (1-65535)"}
    proto = "udp" if proto == "udp" else "tcp"
    action = "deny" if action == "deny" else "allow"

    try:
        if shutil.which("ufw"):
            proc = _run_cmd(["ufw", action, f"{port}/{proto}"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("firewall-cmd"):
            op = "--add-port" if action == "allow" else "--remove-port"
            proc = _run_cmd(["firewall-cmd", "--permanent", op, f"{port}/{proto}"], timeout=10)
            _run_cmd(["firewall-cmd", "--reload"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("iptables"):
            target = "ACCEPT" if action == "allow" else "DROP"
            proc = _run_cmd(["iptables", "-A", "INPUT", "-p", proto, "--dport", str(port), "-j", target], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip() or "Regra aplicada"}
        return {"success": False, "message": "Nenhum firewall (UFW, firewalld, iptables) encontrado"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def toggle_firewall_engine(enable: bool) -> Dict[str, Any]:
    """Ativa ou desativa o firewall detectado no host (UFW ou firewalld)."""
    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" or ("ufw" in info.get("installed_engines", []) and engine_id in ("none", "iptables")):
        ufw_bin = shutil.which("ufw")
        if ufw_bin:
            cmd = [ufw_bin, "--force", "enable"] if enable else [ufw_bin, "disable"]
            proc = _run_cmd(cmd, timeout=15)
            return {"success": proc.returncode == 0, "engine": "UFW", "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" or "firewalld" in info.get("installed_engines", []):
        action = "start" if enable else "stop"
        proc = _run_cmd(["systemctl", action, "firewalld"], timeout=15)
        return {"success": proc.returncode == 0, "engine": "firewalld", "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": "Nenhum gerenciador com ativação automática (UFW ou firewalld) encontrado neste host."}


def delete_firewall_rule(rule_ref: str) -> Dict[str, Any]:
    """Remove uma regra do firewall ativo (UFW, firewalld ou iptables)."""
    rule_ref = str(rule_ref or "").strip()
    if not rule_ref:
        return {"success": False, "error": "Identificador da regra inválido."}

    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" and shutil.which("ufw"):
        if not rule_ref.isdigit():
            return {"success": False, "error": "Número de regra UFW inválido."}
        proc = _run_cmd(["ufw", "--force", "delete", rule_ref], timeout=15)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" and shutil.which("firewall-cmd"):
        if rule_ref.startswith("svc:"):
            svc = rule_ref[4:]
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-service={svc}"], timeout=10)
        else:
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-port={rule_ref}"], timeout=10)
        _run_cmd(["firewall-cmd", "--reload"], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "iptables" and shutil.which("iptables") and rule_ref.isdigit():
        proc = _run_cmd(["iptables", "-D", "INPUT", rule_ref], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": f"Remoção não suportada ou motor '{engine_id}' indisponível."}


def get_backup_file_path(filename: str) -> Optional[str]:
    if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", filename):
        return None
    target = os.path.join(_get_backup_dir(), filename)
    return target if os.path.exists(target) else None

def restore_backup(source: str, target_name: str) -> Dict[str, Any]:
    """Safely restore a local or Cloudflare R2 .tar.gz backup into a recovery folder."""
    bdir = _get_backup_dir()
    local_file: Optional[str] = None
    if source == "r2":
        cfg = _resolve_r2_cfg()
        if not all([cfg["endpoint"], cfg["bucket"], cfg["access_key"], cfg["secret_key"]]):
            return {"success": False, "message": "Cloudflare R2 não configurado"}
        try:
            raw = _s3_signed_request("GET", cfg["endpoint"], cfg["bucket"], target_name, cfg["access_key"], cfg["secret_key"])
            fname = os.path.basename(target_name)
            if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", fname):
                return {"success": False, "message": "Nome de arquivo inválido"}
            local_file = os.path.join(bdir, fname)
            Path(local_file).write_bytes(raw)
        except Exception as exc:
            return {"success": False, "message": f"Erro ao baixar do R2: {exc}"}
    else:
        local_file = get_backup_file_path(target_name)
        if not local_file:
            return {"success": False, "message": "Backup local não encontrado"}

    restore_dir = os.path.join(bdir, "restored", datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(restore_dir, exist_ok=True)
    try:
        with tarfile.open(local_file, "r:gz") as tar:
            for member in tar.getmembers():
                member_path = os.path.abspath(os.path.join(restore_dir, member.name))
                if not member_path.startswith(os.path.abspath(restore_dir) + os.sep) and member_path != os.path.abspath(restore_dir):
                    return {"success": False, "message": f"Caminho inválido bloqueado no arquivo: {member.name}"}
            tar.extractall(path=restore_dir)
        return {"success": True, "restored_to": restore_dir, "message": f"Backup restaurado em {restore_dir}"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def create_api_token(name: str) -> Dict[str, Any]:
    tokens = _read_json("api_tokens.json", [])
    raw_token = f"lmx_{secrets.token_urlsafe(24)}"
    entry = {
        "id": secrets.token_hex(4),
        "name": name.strip() or "Token API",
        "prefix": raw_token[:10] + "...",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tokens.append(entry)
    _write_json("api_tokens.json", tokens)
    return {"token": raw_token, "entry": entry}


def delete_api_token(token_id: str) -> List[Dict[str, Any]]:
    tokens = [t for t in _read_json("api_tokens.json", []) if t.get("id") != token_id]
    _write_json("api_tokens.json", tokens)
    return tokens


# ─── Compliance Audit & Reports ───────────────────────────────────────────────

def run_compliance_audit() -> Dict[str, Any]:
    sec = get_security_overview()
    bkp = get_backup_overview()
    upd = get_cached_updates()
    pending = int((upd.get("updates") or {}).get("pending_count", 0) or 0)
    storage = get_real_storage_info()
    max_disk = max([m.get("percent", 0) for m in storage.get("mounts", [])] or [0])

    # Check SSH root login
    ssh_root = "Permitido/Desconhecido"
    ssh_ok = False
    if os.path.exists("/etc/ssh/sshd_config"):
        try:
            txt = Path("/etc/ssh/sshd_config").read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^\s*PermitRootLogin\s+no", txt, re.MULTILINE):
                ssh_root = "Desabilitado (no)"
                ssh_ok = True
        except OSError:
            pass

    items = [
        {
            "category": "backup",
            "title": "Cobertura de Backup Local",
            "status": "Conforme" if len(bkp.get("backups", [])) > 0 else "Observação",
            "detail": f"{len(bkp.get('backups', []))} arquivo(s) em {bkp.get('destination')}",
        },
        {
            "category": "security",
            "title": "Firewall Ativo no Host",
            "status": "Conforme" if sec["firewall"]["active"] else "Observação",
            "detail": f"Motor: {sec['firewall']['engine']} ({len(sec['firewall']['rules'])} regras)",
        },
        {
            "category": "security",
            "title": "Acesso SSH Root",
            "status": "Conforme" if ssh_ok else "Observação",
            "detail": ssh_root,
        },
        {
            "category": "security",
            "title": "Proteção Fail2Ban",
            "status": "Conforme" if sec["fail2ban"]["installed"] else "Observação",
            "detail": f"{len(sec['fail2ban']['jails'])} jail(s) ativo(s)" if sec["fail2ban"]["installed"] else "Não instalado",
        },
        {
            "category": "system",
            "title": "Atualizações de Segurança Pendentes",
            "status": "Conforme" if pending == 0 else "Observação",
            "detail": f"{pending} pacote(s) aguardando atualização",
        },
        {
            "category": "storage",
            "title": "Capacidade das Partições",
            "status": "Conforme" if max_disk < 85 else "Observação",
            "detail": f"Uso máximo em disco: {max_disk}%",
        },
        {
            "category": "network",
            "title": "Security Gateway (Tailscale)",
            "status": "Conforme" if sec["tailscale"]["running"] else "Não aplicável",
            "detail": f"Conectado ({sec['tailscale']['ip']})" if sec["tailscale"]["running"] else "Tailscale não conectado",
        },
    ]

    return {
        "items": items,
        "counts": {
            "conforme": sum(1 for i in items if i["status"] == "Conforme"),
            "observacao": sum(1 for i in items if i["status"] == "Observação"),
            "nao_aplicavel": sum(1 for i in items if i["status"] == "Não aplicável"),
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ─── Settings & Linked Nodes ──────────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "language": "pt-BR",
    "theme": "dark",
    "network_unit": "bytes",
    "github_token": "",
    "excluded_disks": [],
    "excluded_interfaces": [],
    "quiet_hours": "22:00-07:00",
    "daily_summary_time": "08:00",
    "thresholds": {"cpu_warn": 80, "cpu_crit": 90, "mem_warn": 85, "mem_crit": 95, "temp_warn": 75, "disk_warn": 90},
    "notifications": {"enabled": False, "provider": "telegram", "telegram_token": "", "telegram_chat_id": "", "discord_webhook": "", "gotify_url": "", "gotify_token": "", "apprise_url": ""},
    "ai": {"provider": "openrouter", "api_key": "", "model": "nvidia/nemotron-3-nano-30b-a3b:reasoning:free"},
}


def get_settings() -> Dict[str, Any]:
    saved = _read_json("settings.json", {})
    return {**DEFAULT_SETTINGS, **saved}


def save_settings(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged = {**get_settings(), **payload}
    _write_json("settings.json", merged)
    return merged


def get_linked_nodes() -> List[Dict[str, Any]]:
    return _read_json("linked_nodes.json", [])


def add_linked_node(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes = get_linked_nodes()
    nodes.append({
        "id": secrets.token_hex(4),
        "name": str(node.get("name", "node")).strip(),
        "url": str(node.get("url", "")).strip(),
        "type": str(node.get("type", "Linux Standalone")).strip(),
        "tunnel": bool(node.get("tunnel", False)),
    })
    _write_json("linked_nodes.json", nodes)
    return nodes


def delete_linked_node(node_id: str) -> List[Dict[str, Any]]:
    nodes = [n for n in get_linked_nodes() if n.get("id") != node_id]
    _write_json("linked_nodes.json", nodes)
    return nodes


def get_top_processes(sort_by: str = "cpu", limit: int = 80) -> Dict[str, Any]:
    """Return real running processes sorted by CPU or Memory (RSS) via psutil."""
    import psutil
    procs: List[Dict[str, Any]] = []
    for p in psutil.process_iter(["pid", "username", "cpu_percent", "memory_percent", "memory_info", "name", "cmdline"]):
        try:
            info = p.info
            mem_info = info.get("memory_info")
            rss_kb = int(mem_info.rss / 1024) if mem_info else 0
            cmdline_list = info.get("cmdline") or []
            cmd_full = " ".join(cmdline_list) if cmdline_list else (info.get("name") or "")
            procs.append({
                "pid": info.get("pid"),
                "user": info.get("username") or "-",
                "cpu": round(float(info.get("cpu_percent") or 0.0), 1),
                "mem": round(float(info.get("memory_percent") or 0.0), 1),
                "rss_kb": rss_kb,
                "command": info.get("name") or cmd_full[:40],
                "cmdline": cmd_full[:240],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    key_fn = (lambda x: x["rss_kb"]) if sort_by == "mem" else (lambda x: x["cpu"])
    procs.sort(key=key_fn, reverse=True)
    return {
        "processes": procs[:max(1, min(limit, 200))],
        "sort": sort_by,
        "captured_at": int(time.time()),
    }


def kill_process(pid: int, force: bool = False) -> Dict[str, Any]:
    """Terminate or kill a running process safely by PID."""
    if pid <= 1:
        return {"success": False, "error": "PID crítico do sistema protegido (PID <= 1)"}
    if pid == os.getpid():
        return {"success": False, "error": "Não é permitido encerrar o próprio backend do Linux Menux"}
    import psutil
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        if force:
            proc.kill()
        else:
            proc.terminate()
        return {"success": True, "pid": pid, "name": name, "signal": "SIGKILL" if force else "SIGTERM"}
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Processo {pid} não encontrado"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Permissão negada para encerrar processo {pid}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_interface_detail(iface_name: str) -> Dict[str, Any]:
    """Read real interface statistics and link properties from /sys/class/net."""
    if not re.match(r"^[a-zA-Z0-9_.:-]+$", iface_name):
        return {"error": "Interface inválida"}
    base = Path(f"/sys/class/net/{iface_name}")
    if not base.exists():
        return {"error": "Interface não encontrada"}

    def _read_txt(p: Path, default: str = "N/D") -> str:
        try:
            return p.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            return default

    def _read_int(p: Path) -> int:
        try:
            return int(p.read_text(encoding="utf-8", errors="ignore").strip())
        except (OSError, ValueError):
            return 0

    stats = base / "statistics"
    rx_b = _read_int(stats / "rx_bytes")
    tx_b = _read_int(stats / "tx_bytes")
    speed_raw = _read_txt(base / "speed", "")
    speed_str = f"{speed_raw} Mbps" if speed_raw.isdigit() else "N/D"
    oper = _read_txt(base / "operstate", "unknown")

    return {
        "name": iface_name,
        "status": "Ativo" if oper == "up" else "Inativo",
        "operstate": oper,
        "mac": _read_txt(base / "address"),
        "mtu": _read_int(base / "mtu") or 1500,
        "speed": speed_str,
        "duplex": _read_txt(base / "duplex", "N/D"),
        "rx_bytes_formatted": format_bytes(rx_b),
        "tx_bytes_formatted": format_bytes(tx_b),
        "rx_packets": _read_int(stats / "rx_packets"),
        "tx_packets": _read_int(stats / "tx_packets"),
        "rx_errors": _read_int(stats / "rx_errors"),
        "tx_errors": _read_int(stats / "tx_errors"),
        "rx_dropped": _read_int(stats / "rx_dropped"),
        "tx_dropped": _read_int(stats / "tx_dropped"),
    }


def send_test_notification(provider: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Send a real test message to Telegram or Discord."""
    import urllib.request
    msg = f"🛡️ Linux Menux Monitor ({detect_system_info().get('hostname', 'host')}): Teste de notificação OK!"
    try:
        if provider == "telegram":
            token = str(cfg.get("telegram_token", "")).strip()
            chat_id = str(cfg.get("telegram_chat_id", "")).strip()
            if not token or not chat_id:
                return {"success": False, "message": "Token e Chat ID do Telegram são obrigatórios."}
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = json.dumps({"chat_id": chat_id, "text": msg}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"success": resp.status == 200, "message": "Mensagem enviada ao Telegram!"}
        if provider == "discord":
            webhook = str(cfg.get("discord_webhook", "")).strip()
            if not webhook.startswith("https://"):
                return {"success": False, "message": "URL do Webhook Discord inválida."}
            data = json.dumps({"content": msg}).encode("utf-8")
            req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"success": resp.status in (200, 204), "message": "Mensagem enviada ao Discord!"}
        return {"success": False, "message": "Provedor inválido"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def add_firewall_rule(port: str, proto: str = "tcp", action: str = "allow") -> Dict[str, Any]:
    """Add a firewall rule safely across UFW, firewalld, or iptables."""
    if not re.match(r"^\d{1,5}$", str(port)) or not (1 <= int(port) <= 65535):
        return {"success": False, "message": "Porta inválida (1-65535)"}
    proto = "udp" if proto == "udp" else "tcp"
    action = "deny" if action == "deny" else "allow"

    try:
        if shutil.which("ufw"):
            proc = _run_cmd(["ufw", action, f"{port}/{proto}"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("firewall-cmd"):
            op = "--add-port" if action == "allow" else "--remove-port"
            proc = _run_cmd(["firewall-cmd", "--permanent", op, f"{port}/{proto}"], timeout=10)
            _run_cmd(["firewall-cmd", "--reload"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("iptables"):
            target = "ACCEPT" if action == "allow" else "DROP"
            proc = _run_cmd(["iptables", "-A", "INPUT", "-p", proto, "--dport", str(port), "-j", target], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip() or "Regra aplicada"}
        return {"success": False, "message": "Nenhum firewall (UFW, firewalld, iptables) encontrado"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def toggle_firewall_engine(enable: bool) -> Dict[str, Any]:
    """Ativa ou desativa o firewall detectado no host (UFW ou firewalld)."""
    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" or ("ufw" in info.get("installed_engines", []) and engine_id in ("none", "iptables")):
        ufw_bin = shutil.which("ufw")
        if ufw_bin:
            cmd = [ufw_bin, "--force", "enable"] if enable else [ufw_bin, "disable"]
            proc = _run_cmd(cmd, timeout=15)
            return {"success": proc.returncode == 0, "engine": "UFW", "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" or "firewalld" in info.get("installed_engines", []):
        action = "start" if enable else "stop"
        proc = _run_cmd(["systemctl", action, "firewalld"], timeout=15)
        return {"success": proc.returncode == 0, "engine": "firewalld", "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": "Nenhum gerenciador com ativação automática (UFW ou firewalld) encontrado neste host."}


def delete_firewall_rule(rule_ref: str) -> Dict[str, Any]:
    """Remove uma regra do firewall ativo (UFW, firewalld ou iptables)."""
    rule_ref = str(rule_ref or "").strip()
    if not rule_ref:
        return {"success": False, "error": "Identificador da regra inválido."}

    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" and shutil.which("ufw"):
        if not rule_ref.isdigit():
            return {"success": False, "error": "Número de regra UFW inválido."}
        proc = _run_cmd(["ufw", "--force", "delete", rule_ref], timeout=15)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" and shutil.which("firewall-cmd"):
        if rule_ref.startswith("svc:"):
            svc = rule_ref[4:]
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-service={svc}"], timeout=10)
        else:
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-port={rule_ref}"], timeout=10)
        _run_cmd(["firewall-cmd", "--reload"], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "iptables" and shutil.which("iptables") and rule_ref.isdigit():
        proc = _run_cmd(["iptables", "-D", "INPUT", rule_ref], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": f"Remoção não suportada ou motor '{engine_id}' indisponível."}


def get_backup_file_path(filename: str) -> Optional[str]:
    if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", filename):
        return None
    target = os.path.join(_get_backup_dir(), filename)
    return target if os.path.exists(target) else None

def restore_backup(source: str, target_name: str) -> Dict[str, Any]:
    """Safely restore a local or Cloudflare R2 .tar.gz backup into a recovery folder."""
    bdir = _get_backup_dir()
    local_file: Optional[str] = None
    if source == "r2":
        cfg = _resolve_r2_cfg()
        if not all([cfg["endpoint"], cfg["bucket"], cfg["access_key"], cfg["secret_key"]]):
            return {"success": False, "message": "Cloudflare R2 não configurado"}
        try:
            raw = _s3_signed_request("GET", cfg["endpoint"], cfg["bucket"], target_name, cfg["access_key"], cfg["secret_key"])
            fname = os.path.basename(target_name)
            if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", fname):
                return {"success": False, "message": "Nome de arquivo inválido"}
            local_file = os.path.join(bdir, fname)
            Path(local_file).write_bytes(raw)
        except Exception as exc:
            return {"success": False, "message": f"Erro ao baixar do R2: {exc}"}
    else:
        local_file = get_backup_file_path(target_name)
        if not local_file:
            return {"success": False, "message": "Backup local não encontrado"}

    restore_dir = os.path.join(bdir, "restored", datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(restore_dir, exist_ok=True)
    try:
        with tarfile.open(local_file, "r:gz") as tar:
            for member in tar.getmembers():
                member_path = os.path.abspath(os.path.join(restore_dir, member.name))
                if not member_path.startswith(os.path.abspath(restore_dir) + os.sep) and member_path != os.path.abspath(restore_dir):
                    return {"success": False, "message": f"Caminho inválido bloqueado no arquivo: {member.name}"}
            tar.extractall(path=restore_dir)
        return {"success": True, "restored_to": restore_dir, "message": f"Backup restaurado em {restore_dir}"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}

def restore_backup(source: str, target_name: str) -> Dict[str, Any]:
    """Safely restore a local or Cloudflare R2 .tar.gz backup into a recovery folder."""
    bdir = _get_backup_dir()
    local_file: Optional[str] = None
    if source == "r2":
        cfg = _resolve_r2_cfg()
        if not all([cfg["endpoint"], cfg["bucket"], cfg["access_key"], cfg["secret_key"]]):
            return {"success": False, "message": "Cloudflare R2 não configurado"}
        try:
            raw = _s3_signed_request("GET", cfg["endpoint"], cfg["bucket"], target_name, cfg["access_key"], cfg["secret_key"])
            fname = os.path.basename(target_name)
            if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", fname):
                return {"success": False, "message": "Nome de arquivo inválido"}
            local_file = os.path.join(bdir, fname)
            Path(local_file).write_bytes(raw)
        except Exception as exc:
            return {"success": False, "message": f"Erro ao baixar do R2: {exc}"}
    else:
        local_file = get_backup_file_path(target_name)
        if not local_file:
            return {"success": False, "message": "Backup local não encontrado"}

    restore_dir = os.path.join(bdir, "restored", datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(restore_dir, exist_ok=True)
    try:
        with tarfile.open(local_file, "r:gz") as tar:
            for member in tar.getmembers():
                member_path = os.path.abspath(os.path.join(restore_dir, member.name))
                if not member_path.startswith(os.path.abspath(restore_dir) + os.sep) and member_path != os.path.abspath(restore_dir):
                    return {"success": False, "message": f"Caminho inválido bloqueado no arquivo: {member.name}"}
            tar.extractall(path=restore_dir)
        return {"success": True, "restored_to": restore_dir, "message": f"Backup restaurado em {restore_dir}"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def save_smart_schedule(item: Dict[str, Any]) -> Dict[str, Any]:
    data = _read_json("smart_schedules.json", {"enabled": True, "items": []})
    items = data.get("items", [])
    items.append({
        "id": secrets.token_hex(4),
        "device": item.get("device", "/dev/sda"),
        "mode": item.get("mode", "short"),
        "cron": item.get("cron", "0 3 * * 0"),
        "enabled": True,
    })
    data["items"] = items
    _write_json("smart_schedules.json", data)
    return data


# ─── Full Hardware Detection ──────────────────────────────────────────────────

def get_full_hardware() -> Dict[str, Any]:
    info = detect_system_info()
    cpu = get_real_cpu_metrics()
    mem = get_real_memory_metrics()
    temp = get_real_temperature()
    storage = get_real_storage_info()
    net = get_real_network_info()

    # CPU extra from lscpu
    l3_cache = "N/D"
    virt_support = "N/D"
    try:
        lp = _run_cmd(["lscpu"], timeout=5)
        if lp.returncode == 0:
            for line in lp.stdout.splitlines():
                if "L3 cache:" in line or "Cache L3:" in line:
                    l3_cache = line.split(":", 1)[1].strip()
                elif "Virtualization:" in line or "Virtualização:" in line:
                    virt_support = line.split(":", 1)[1].strip()
    except Exception:
        pass

    # GPUs & PCI via lspci
    gpus: List[Dict[str, str]] = []
    pci_devices: List[Dict[str, str]] = []
    lspci_bin = shutil.which("lspci")
    if lspci_bin:
        try:
            pp = _run_cmd([lspci_bin, "-k"], timeout=6)
            current: Optional[Dict[str, str]] = None
            for line in pp.stdout.splitlines():
                if not line.startswith("\t") and not line.startswith(" "):
                    parts = line.split(" ", 1)
                    slot = parts[0]
                    desc = parts[1] if len(parts) > 1 else line
                    low = desc.lower()
                    if any(k in low for k in ("vga", "3d", "display", "graphics")):
                        cat = "Placa gráfica"
                    elif "usb" in low:
                        cat = "Controlador USB"
                    elif any(k in low for k in ("sata", "nvme", "ahci", "raid", "storage", "non-volatile memory")):
                        cat = "Controlador de armazenamento"
                    elif "audio" in low:
                        cat = "Controlador de áudio"
                    elif any(k in low for k in ("ethernet", "network", "wireless", "wi-fi", "wifi")):
                        cat = "Controlador de rede"
                    else:
                        cat = "Dispositivo PCI"
                    current = {"slot": slot, "description": desc, "driver": "N/D", "category": cat}
                    pci_devices.append(current)
                    if cat == "Placa gráfica":
                        gpus.append(current)
                elif current and "Kernel driver in use:" in line:
                    current["driver"] = line.split(":", 1)[1].strip()
        except Exception:
            pass

    # Thermal sensors from /sys/class/hwmon
    sensors: List[Dict[str, Any]] = []
    hwmon_root = Path("/sys/class/hwmon")
    if hwmon_root.exists():
        for h in sorted(hwmon_root.iterdir()):
            chip = ""
            name_f = h / "name"
            if name_f.exists():
                chip = name_f.read_text(encoding="utf-8", errors="ignore").strip()
            for tf in sorted(h.glob("temp*_input")):
                try:
                    val = int(tf.read_text().strip()) / 1000.0
                    lbl_f = h / tf.name.replace("_input", "_label")
                    lbl = lbl_f.read_text(encoding="utf-8", errors="ignore").strip() if lbl_f.exists() else tf.name
                    if 0 < val < 130:
                        c_low = chip.lower()
                        grp = "NVME" if "nvme" in c_low else ("CPU" if any(k in c_low for k in ("coretemp", "k10temp", "zenpower", "cpu")) else "Outro")
                        sensors.append({"chip": chip, "label": lbl, "temp_c": round(val, 1), "group": grp})
                except Exception:
                    pass

    # Memory modules via dmidecode (best effort)
    dimms: List[Dict[str, str]] = []
    dmi_bin = shutil.which("dmidecode")
    if dmi_bin:
        try:
            dp = _run_cmd([dmi_bin, "-t", "memory"], timeout=5)
            if dp.returncode == 0:
                blocks = dp.stdout.split("Memory Device")
                for b in blocks[1:]:
                    size_m = re.search(r"Size:\s*(.+)", b)
                    if not size_m or "No Module" in size_m.group(1):
                        continue
                    loc_m = re.search(r"Locator:\s*(.+)", b)
                    spd_m = re.search(r"Speed:\s*(.+)", b)
                    typ_m = re.search(r"Type:\s*(.+)", b)
                    mfg_m = re.search(r"Manufacturer:\s*(.+)", b)
                    dimms.append({
                        "slot": loc_m.group(1).strip() if loc_m else "DIMM",
                        "size": size_m.group(1).strip(),
                        "speed": spd_m.group(1).strip() if spd_m else "N/D",
                        "type": typ_m.group(1).strip() if typ_m else "RAM",
                        "manufacturer": mfg_m.group(1).strip() if mfg_m else "N/D",
                    })
        except Exception:
            pass

    # Motherboard / BIOS from DMI sysfs
    def _dmi(fname: str) -> str:
        try:
            p = Path(f"/sys/class/dmi/id/{fname}")
            return p.read_text(encoding="utf-8", errors="ignore").strip() if p.exists() else "N/D"
        except OSError:
            return "N/D"

    motherboard = {
        "vendor": _dmi("board_vendor"),
        "model": _dmi("board_name"),
        "bios_vendor": _dmi("bios_vendor"),
        "bios_version": _dmi("bios_version"),
        "bios_date": _dmi("bios_date"),
    }

    # Power consumption via Intel RAPL (best effort)
    power_watts: Optional[float] = None
    rapl_path = Path("/sys/class/powercap/intel-rapl:0/energy_uj")
    if rapl_path.exists():
        try:
            e1 = int(rapl_path.read_text().strip())
            t1 = time.monotonic()
            time.sleep(0.15)
            e2 = int(rapl_path.read_text().strip())
            t2 = time.monotonic()
            if e2 >= e1 and (t2 - t1) > 0:
                power_watts = round(((e2 - e1) / 1_000_000.0) / (t2 - t1), 1)
        except Exception:
            pass

    # USB devices via lsusb
    usb_devices: List[Dict[str, str]] = []
    lsusb_bin = shutil.which("lsusb")
    if lsusb_bin:
        try:
            up = _run_cmd([lsusb_bin], timeout=5)
            if up.returncode == 0:
                for line in up.stdout.splitlines():
                    m = re.match(r"Bus\s+(\d+)\s+Device\s+(\d+):\s+ID\s+([0-9a-fA-F:]+)\s*(.*)", line.strip())
                    if m:
                        desc = m.group(4).strip() or f"USB {m.group(3)}"
                        if "root hub" in desc.lower():
                            continue
                        usb_devices.append({
                            "bus": m.group(1),
                            "device": m.group(2),
                            "usb_id": m.group(3),
                            "description": desc,
                        })
        except Exception:
            pass

    return {
        "system": info,
        "cpu": {**cpu, "l3_cache": l3_cache, "virtualization": virt_support},
        "motherboard": motherboard,
        "power": {"cpu_watts": power_watts},
        "memory": mem,
        "dimms": dimms,
        "temperature": temp,
        "sensors": sensors[:24],
        "gpus": gpus,
        "pci_devices": pci_devices[:30],
        "network_summary": [
            i for i in net.get("interfaces", [])
            if not i.get("name", "").startswith(("lo", "veth", "br-", "docker"))
        ],
        "storage_summary": storage.get("physical_disks", []),
        "usb_devices": usb_devices,
    }


# ─── Backup Operations ────────────────────────────────────────────────────────

def _get_backup_dir() -> str:
    try:
        os.makedirs(DEFAULT_BACKUP_DIR, exist_ok=True)
        return DEFAULT_BACKUP_DIR
    except OSError:
        fallback = os.path.join(DATA_DIR, "backups")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def get_backup_overview() -> Dict[str, Any]:
    bdir = _get_backup_dir()
    usage = shutil.disk_usage(bdir)
    cfg = _read_json("backup_config.json", {"custom_paths": [], "schedule": "0 3 * * *"})
    files: List[Dict[str, Any]] = []
    for entry in sorted(Path(bdir).glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True):
        st = entry.stat()
        files.append({
            "name": entry.name,
            "path": str(entry),
            "size_bytes": st.st_size,
            "size_formatted": format_bytes(st.st_size),
            "created_at": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {
        "destination": bdir,
        "total_formatted": format_bytes(usage.total),
        "used_formatted": format_bytes(usage.used),
        "free_formatted": format_bytes(usage.free),
        "used_percent": round((usage.used / usage.total) * 100, 1) if usage.total else 0,
        "custom_paths": cfg.get("custom_paths", []),
        "schedule": cfg.get("schedule", "0 3 * * *"),
        "backups": files,
    }


def add_backup_path(path_str: str) -> Dict[str, Any]:
    cfg = _read_json("backup_config.json", {"custom_paths": [], "schedule": "0 3 * * *"})
    p = path_str.strip()
    if p and p not in cfg["custom_paths"] and os.path.exists(p):
        cfg["custom_paths"].append(p)
        _write_json("backup_config.json", cfg)
    return cfg


def remove_backup_path(path_str: str) -> Dict[str, Any]:
    cfg = _read_json("backup_config.json", {"custom_paths": [], "schedule": "0 3 * * *"})
    cfg["custom_paths"] = [x for x in cfg.get("custom_paths", []) if x != path_str]
    _write_json("backup_config.json", cfg)
    return cfg


def run_manual_backup(paths: Optional[List[str]] = None) -> Dict[str, Any]:
    bdir = _get_backup_dir()
    cfg = _read_json("backup_config.json", {"custom_paths": []})
    targets = paths or cfg.get("custom_paths") or [DATA_DIR]
    valid_targets = [t for t in targets if os.path.exists(t)]
    if not valid_targets:
        valid_targets = [DATA_DIR]

    fname = f"linuxmenux-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tar.gz"
    dest = os.path.join(bdir, fname)
    try:
        with tarfile.open(dest, "w:gz") as tar:
            for t in valid_targets:
                tar.add(t, arcname=os.path.basename(t.rstrip("/")) or "data")
        return {"success": True, "filename": fname, "path": dest, "size_formatted": format_bytes(os.path.getsize(dest))}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def add_firewall_rule(port: str, proto: str = "tcp", action: str = "allow") -> Dict[str, Any]:
    """Add a firewall rule safely across UFW, firewalld, or iptables."""
    if not re.match(r"^\d{1,5}$", str(port)) or not (1 <= int(port) <= 65535):
        return {"success": False, "message": "Porta inválida (1-65535)"}
    proto = "udp" if proto == "udp" else "tcp"
    action = "deny" if action == "deny" else "allow"

    try:
        if shutil.which("ufw"):
            proc = _run_cmd(["ufw", action, f"{port}/{proto}"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("firewall-cmd"):
            op = "--add-port" if action == "allow" else "--remove-port"
            proc = _run_cmd(["firewall-cmd", "--permanent", op, f"{port}/{proto}"], timeout=10)
            _run_cmd(["firewall-cmd", "--reload"], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip()}
        if shutil.which("iptables"):
            target = "ACCEPT" if action == "allow" else "DROP"
            proc = _run_cmd(["iptables", "-A", "INPUT", "-p", proto, "--dport", str(port), "-j", target], timeout=10)
            return {"success": proc.returncode == 0, "message": (proc.stdout or proc.stderr).strip() or "Regra aplicada"}
        return {"success": False, "message": "Nenhum firewall (UFW, firewalld, iptables) encontrado"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def toggle_firewall_engine(enable: bool) -> Dict[str, Any]:
    """Ativa ou desativa o firewall detectado no host (UFW ou firewalld)."""
    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" or ("ufw" in info.get("installed_engines", []) and engine_id in ("none", "iptables")):
        ufw_bin = shutil.which("ufw")
        if ufw_bin:
            cmd = [ufw_bin, "--force", "enable"] if enable else [ufw_bin, "disable"]
            proc = _run_cmd(cmd, timeout=15)
            return {"success": proc.returncode == 0, "engine": "UFW", "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" or "firewalld" in info.get("installed_engines", []):
        action = "start" if enable else "stop"
        proc = _run_cmd(["systemctl", action, "firewalld"], timeout=15)
        return {"success": proc.returncode == 0, "engine": "firewalld", "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": "Nenhum gerenciador com ativação automática (UFW ou firewalld) encontrado neste host."}


def delete_firewall_rule(rule_ref: str) -> Dict[str, Any]:
    """Remove uma regra do firewall ativo (UFW, firewalld ou iptables)."""
    rule_ref = str(rule_ref or "").strip()
    if not rule_ref:
        return {"success": False, "error": "Identificador da regra inválido."}

    info = _inspect_firewall_smart()
    engine_id = info.get("engine_id", "none")

    if engine_id == "ufw" and shutil.which("ufw"):
        if not rule_ref.isdigit():
            return {"success": False, "error": "Número de regra UFW inválido."}
        proc = _run_cmd(["ufw", "--force", "delete", rule_ref], timeout=15)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "firewalld" and shutil.which("firewall-cmd"):
        if rule_ref.startswith("svc:"):
            svc = rule_ref[4:]
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-service={svc}"], timeout=10)
        else:
            proc = _run_cmd(["firewall-cmd", "--permanent", f"--remove-port={rule_ref}"], timeout=10)
        _run_cmd(["firewall-cmd", "--reload"], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    if engine_id == "iptables" and shutil.which("iptables") and rule_ref.isdigit():
        proc = _run_cmd(["iptables", "-D", "INPUT", rule_ref], timeout=10)
        return {"success": proc.returncode == 0, "output": (proc.stdout + proc.stderr).strip()}

    return {"success": False, "error": f"Remoção não suportada ou motor '{engine_id}' indisponível."}


def get_backup_file_path(filename: str) -> Optional[str]:
    if not re.match(r"^[a-zA-Z0-9._-]+\.tar\.gz$", filename):
        return None
    target = os.path.join(_get_backup_dir(), filename)
    return target if os.path.exists(target) else None


# ─── App Overrides (Edit/Hide Auto-Detected Container Apps) ───────────────────

def get_app_overrides() -> Dict[str, Any]:
    return _read_json("app_overrides.json", {})


def save_app_override(app_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    overrides = get_app_overrides()
    overrides[app_id] = {
        "name": str(payload.get("name", "")).strip(),
        "url": str(payload.get("url", "")).strip(),
        "category": str(payload.get("category", "Geral")).strip() or "Geral",
        "description": str(payload.get("description", "")).strip(),
        "hidden": bool(payload.get("hidden", False)),
    }
    _write_json("app_overrides.json", overrides)
    return overrides


# ─── Backup Destinations (Local, Borg, Cloudflare R2 / S3) ────────────────────

def get_backup_destinations() -> Dict[str, Any]:
    return _read_json(
        "backup_destinations.json",
        {
            "active_type": "local",
            "local": {"path": _get_backup_dir()},
            "borg": {"repo": "", "passphrase": ""},
            "r2": {"account_id": "", "endpoint": "", "bucket": "", "access_key": "", "secret_key": "", "prefix": "linuxmenux/"},
        },
    )


def save_backup_destinations(payload: Dict[str, Any]) -> Dict[str, Any]:
    cur = get_backup_destinations()
    if "active_type" in payload:
        cur["active_type"] = str(payload["active_type"])
    for key in ("local", "borg", "r2"):
        if isinstance(payload.get(key), dict):
            cur[key] = {**cur.get(key, {}), **payload[key]}
    _write_json("backup_destinations.json", cur)
    return cur


def _s3_signed_request(
    method: str,
    endpoint: str,
    bucket: str,
    object_key: str,
    access_key: str,
    secret_key: str,
    query: str = "",
    body: bytes = b"",
    region: str = "auto",
) -> bytes:
    import hashlib
    import hmac
    import urllib.parse
    import urllib.request

    ep = endpoint.rstrip("/")
    parsed = urllib.parse.urlparse(ep)
    host = parsed.netloc
    clean_key = object_key.lstrip("/")
    canonical_uri = f"/{bucket}" + (f"/{urllib.parse.quote(clean_key, safe='/')}" if clean_key else "")
    t = datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(body).hexdigest()

    canonical_headers = f"host:{host}\nx-amz-content-sha256:{payload_hash}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    canonical_request = f"{method}\n{canonical_uri}\n{query}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

    credential_scope = f"{date_stamp}/{region}/s3/aws4_request"
    string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"

    def _sign(key_bytes: bytes, msg: str) -> bytes:
        return hmac.new(key_bytes, msg.encode("utf-8"), hashlib.sha256).digest()

    k_date = _sign(("AWS4" + secret_key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, "s3")
    k_signing = _sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    auth_header = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    url = f"{ep}{canonical_uri}" + (f"?{query}" if query else "")
    req = urllib.request.Request(
        url,
        data=body if method in ("PUT", "POST") else None,
        method=method,
        headers={
            "Host": host,
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": auth_header,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def _resolve_r2_cfg() -> Dict[str, str]:
    r2 = get_backup_destinations().get("r2", {})
    endpoint = str(r2.get("endpoint") or "").strip()
    account_id = str(r2.get("account_id") or "").strip()
    if not endpoint and account_id:
        endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    return {
        "endpoint": endpoint,
        "bucket": str(r2.get("bucket") or "").strip(),
        "access_key": str(r2.get("access_key") or "").strip(),
        "secret_key": str(r2.get("secret_key") or "").strip(),
        "prefix": str(r2.get("prefix") or "linuxmenux/").strip().lstrip("/"),
    }


def r2_list_backups() -> Dict[str, Any]:
    import xml.etree.ElementTree as ET
    cfg = _resolve_r2_cfg()
    if not all([cfg["endpoint"], cfg["bucket"], cfg["access_key"], cfg["secret_key"]]):
        return {"configured": False, "items": []}
    try:
        raw = _s3_signed_request("GET", cfg["endpoint"], cfg["bucket"], "", cfg["access_key"], cfg["secret_key"], query="list-type=2")
        root = ET.fromstring(raw)
        ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
        items = []
        for c in root.findall(f"{ns}Contents"):
            key = c.findtext(f"{ns}Key") or ""
            if not key.endswith(".tar.gz"):
                continue
            size = int(c.findtext(f"{ns}Size") or 0)
            mod = c.findtext(f"{ns}LastModified") or ""
            items.append({
                "key": key,
                "name": os.path.basename(key),
                "size_bytes": size,
                "size_formatted": format_bytes(size),
                "last_modified": mod[:19].replace("T", " "),
            })
        return {"configured": True, "items": items}
    except Exception as exc:
        return {"configured": True, "items": [], "error": str(exc)}


def r2_upload_backup(filename: str) -> Dict[str, Any]:
    fpath = get_backup_file_path(filename)
    if not fpath:
        return {"success": False, "message": "Arquivo de backup local não encontrado"}
    cfg = _resolve_r2_cfg()
    if not all([cfg["endpoint"], cfg["bucket"], cfg["access_key"], cfg["secret_key"]]):
        return {"success": False, "message": "Cloudflare R2 não configurado"}
    try:
        data = Path(fpath).read_bytes()
        obj_key = f"{cfg['prefix'].rstrip('/')}/{filename}" if cfg["prefix"] else filename
        _s3_signed_request("PUT", cfg["endpoint"], cfg["bucket"], obj_key, cfg["access_key"], cfg["secret_key"], body=data)
        return {"success": True, "key": obj_key, "message": f"Enviado para R2: {obj_key}"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}
