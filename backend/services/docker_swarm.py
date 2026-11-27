"""
Linux Menux Docker Engine, Compose & Swarm Monitor
Natively communicates with /var/run/docker.sock to inspect Docker Swarm clusters,
Dokploy Stacks, Compose Projects, and Containers.
"""

import http.client
import json
import re
import shutil
import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional


class UnixSocketHTTPConnection(http.client.HTTPConnection):
    """HTTP Connection over a Unix domain socket without external dependencies."""
    def __init__(self, socket_path: str, timeout: int = 10):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.socket_path)


class DockerClient:
    """Lightweight Docker Engine, Compose & Swarm API client using the local Unix domain socket."""
    def __init__(self, socket_path: str = "/var/run/docker.sock"):
        import os
        candidates = [
            os.environ.get("DOCKER_HOST", "").replace("unix://", ""),
            socket_path,
            "/run/docker.sock",
        ]
        self.socket_path = next((p for p in candidates if p and os.path.exists(p)), socket_path)

    def request(self, path: str, method: str = "GET", body: Optional[bytes] = None) -> Any:
        try:
            conn = UnixSocketHTTPConnection(self.socket_path, timeout=8)
            headers = {"Host": "localhost", "Accept": "application/json"}
            if body:
                headers["Content-Type"] = "application/json"
            conn.request(method, path, body=body, headers=headers)
            res = conn.getresponse()
            data = res.read()
            conn.close()
            if res.status >= 400:
                return {"error": f"HTTP {res.status}: {data.decode('utf-8', errors='ignore')}"}
            try:
                return json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                return data.decode("utf-8")
        except Exception as e:
            return {"error": str(e)}


docker_cli = DockerClient()


def _extract_traefik_domains(labels: Dict[str, str]) -> List[str]:
    """Extract public domains configured via Traefik in Dokploy."""
    domains = []
    for k, v in labels.items():
        if "traefik.http.routers." in k and ".rule" in k:
            # Matches Host(`example.com`) or Host("example.com")
            matches = re.findall(r"Host\([`'\"]([^`'\"]+)[`'\"]\)", v)
            for m in matches:
                domains.extend([d.strip() for d in m.split(",") if d.strip()])
    return list(set(domains))


def get_docker_overview() -> Dict[str, Any]:
    """Returns general Docker Engine, Compose, and Swarm state."""
    info = docker_cli.request("/info")
    if isinstance(info, dict) and "error" in info:
        return {
            "available": False,
            "error": info["error"],
            "is_swarm": False,
            "containers_total": 0,
            "containers_running": 0,
            "images_count": 0,
        }

    swarm_info = info.get("Swarm", {})
    is_swarm = swarm_info.get("LocalNodeState") == "active"
    control_available = swarm_info.get("ControlAvailable", False)

    return {
        "available": True,
        "server_version": info.get("ServerVersion", "Unknown"),
        "is_swarm": is_swarm,
        "is_manager": control_available,
        "node_id": swarm_info.get("NodeID", ""),
        "containers_total": info.get("Containers", 0),
        "containers_running": info.get("ContainersRunning", 0),
        "containers_paused": info.get("ContainersPaused", 0),
        "containers_stopped": info.get("ContainersStopped", 0),
        "images_count": info.get("Images", 0),
        "cpus": info.get("NCPU", 0),
        "memory_total": info.get("MemTotal", 0),
    }


def list_swarm_services() -> List[Dict[str, Any]]:
    """List Docker Swarm services, including replicas and dokploy stack namespaces."""
    raw = docker_cli.request("/services")
    if not isinstance(raw, list):
        return []

    services = []
    for svc in raw:
        spec = svc.get("Spec", {})
        mode = spec.get("Mode", {})
        replicas = mode.get("Replicated", {}).get("Replicas", 1)
        labels = spec.get("Labels", {})
        stack = labels.get("com.docker.stack.namespace", labels.get("dokploy.appName", "default"))
        traefik_domains = _extract_traefik_domains(labels)

        services.append({
            "id": svc.get("ID"),
            "name": spec.get("Name"),
            "stack": stack,
            "type": "swarm",
            "is_dokploy": bool(labels.get("dokploy.appName") or labels.get("dokploy.projectName")),
            "dokploy_app": labels.get("dokploy.appName", ""),
            "image": spec.get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image", "").split("@")[0],
            "replicas_target": replicas,
            "traefik_domains": traefik_domains,
            "created_at": svc.get("CreatedAt"),
            "updated_at": svc.get("UpdatedAt"),
            "labels": labels,
        })
    return services


def _fmt_bytes_short(b: int) -> str:
    if b <= 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}" if unit != "B" else f"{int(b)} B"
        b /= 1024
    return f"{b:.1f} PB"


def _get_single_container_stats(container_id: str) -> Dict[str, Any]:
    """Fetch live CPU, memory, net I/O and block I/O directly via Docker Unix socket."""
    empty = {
        "cpu_percent": 0.0,
        "mem_percent": 0.0,
        "mem_usage": "0 B / 0 B",
        "net_rx": "0 B",
        "net_tx": "0 B",
        "block_read": "0 B",
        "block_write": "0 B",
    }
    stats = docker_cli.request(f"/containers/{container_id}/stats?stream=false")
    if not isinstance(stats, dict) or "error" in stats:
        return empty
    cpu_stats = stats.get("cpu_stats") or {}
    pre_cpu = stats.get("precpu_stats") or {}
    cpu_delta = (cpu_stats.get("cpu_usage", {}).get("total_usage", 0) or 0) - (
        pre_cpu.get("cpu_usage", {}).get("total_usage", 0) or 0
    )
    sys_delta = (cpu_stats.get("system_cpu_usage", 0) or 0) - (
        pre_cpu.get("system_cpu_usage", 0) or 0
    )
    online_cpus = cpu_stats.get("online_cpus") or len(cpu_stats.get("cpu_usage", {}).get("percpu_usage") or []) or 1
    cpu_pct = round((cpu_delta / sys_delta) * online_cpus * 100.0, 2) if (sys_delta > 0 and cpu_delta > 0) else 0.0

    mem_stats = stats.get("memory_stats") or {}
    mem_used = int(mem_stats.get("usage", 0) or 0)
    mem_limit = int(mem_stats.get("limit", 0) or 0)
    mem_pct = round((mem_used / mem_limit) * 100.0, 1) if mem_limit > 0 else 0.0

    net_rx = sum(int(v.get("rx_bytes", 0) or 0) for v in (stats.get("networks") or {}).values())
    net_tx = sum(int(v.get("tx_bytes", 0) or 0) for v in (stats.get("networks") or {}).values())

    blk_read = 0
    blk_write = 0
    for blk in (stats.get("blkio_stats") or {}).get("io_service_bytes_recursive") or []:
        op = (blk.get("op") or "").lower()
        val = int(blk.get("value", 0) or 0)
        if op == "read":
            blk_read += val
        elif op == "write":
            blk_write += val

    return {
        "cpu_percent": cpu_pct,
        "mem_percent": mem_pct,
        "mem_usage": f"{_fmt_bytes_short(mem_used)} / {_fmt_bytes_short(mem_limit)}",
        "net_rx": _fmt_bytes_short(net_rx),
        "net_tx": _fmt_bytes_short(net_tx),
        "block_read": _fmt_bytes_short(blk_read),
        "block_write": _fmt_bytes_short(blk_write),
    }


def _collect_docker_cli_stats() -> Dict[str, Dict[str, Any]]:
    """Fast single-call stats collection via docker CLI for all running containers."""
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return {}
    try:
        proc = subprocess.run(
            [docker_bin, "stats", "--no-stream", "--no-trunc", "--format", "{{.ID}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}"],
            capture_output=True,
            text=True,
            timeout=12,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        for line in proc.stdout.splitlines():
            parts = line.strip().split("|")
            if len(parts) < 6:
                continue
            sid = parts[0][:12]
            cpu_str = parts[1].replace("%", "").strip()
            mem_usage = parts[2].strip()
            mem_pct_str = parts[3].replace("%", "").strip()
            net_parts = [p.strip() for p in parts[4].split("/")]
            blk_parts = [p.strip() for p in parts[5].split("/")]
            try:
                cpu_val = round(float(cpu_str), 2)
            except ValueError:
                cpu_val = 0.0
            try:
                mem_pct_val = round(float(mem_pct_str), 1)
            except ValueError:
                mem_pct_val = 0.0
            out[sid] = {
                "cpu_percent": cpu_val,
                "mem_percent": mem_pct_val,
                "mem_usage": mem_usage or "0 B / 0 B",
                "net_rx": net_parts[0] if len(net_parts) > 0 else "0 B",
                "net_tx": net_parts[1] if len(net_parts) > 1 else "0 B",
                "block_read": blk_parts[0] if len(blk_parts) > 0 else "0 B",
                "block_write": blk_parts[1] if len(blk_parts) > 1 else "0 B",
            }
        return out
    except Exception:
        return {}


def _list_containers_via_cli(all_containers: bool = True) -> List[Dict[str, Any]]:
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return []
    cmd = [docker_bin, "ps", "--no-trunc", "--format", "{{json .}}"]
    if all_containers:
        cmd.insert(2, "-a")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        items: List[Dict[str, Any]] = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = row.get("ID", "")
            labels_raw = row.get("Labels", "") or ""
            labels: Dict[str, str] = {}
            for pair in labels_raw.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    labels[k.strip()] = v.strip()
            items.append({
                "Id": cid,
                "Names": [f"/{row.get('Names', cid[:12])}"],
                "Image": row.get("Image", ""),
                "State": (row.get("State") or "").lower() or ("running" if "Up" in (row.get("Status") or "") else "exited"),
                "Status": row.get("Status", ""),
                "Labels": labels,
                "Created": 0,
                "Ports": [],
            })
        return items
    except Exception:
        return []


def list_containers(all_containers: bool = True) -> List[Dict[str, Any]]:
    """List all containers on the host with status, Dokploy metadata, live stats, and Traefik domains."""
    path = f"/containers/json?all={'true' if all_containers else 'false'}"
    raw = docker_cli.request(path)
    if not isinstance(raw, list):
        raw = _list_containers_via_cli(all_containers=all_containers)
    if not isinstance(raw, list):
        return []

    running_sids = [c.get("Id", "")[:12] for c in raw if c.get("State") == "running" and c.get("Id")]
    stats_map: Dict[str, Dict[str, Any]] = {}
    if running_sids:
        stats_map = _collect_docker_cli_stats()
        missing_sids = [sid for sid in running_sids if sid not in stats_map]
        if missing_sids:
            with ThreadPoolExecutor(max_workers=min(8, len(missing_sids))) as pool:
                futures = {pool.submit(_get_single_container_stats, sid): sid for sid in missing_sids}
                for fut, sid in futures.items():
                    try:
                        stats_map[sid] = fut.result(timeout=10)
                    except Exception:
                        pass
    result = []
    for c in raw:
        names = [n.lstrip("/") for n in c.get("Names", [])]
        name = names[0] if names else c.get("Id", "")[:12]
        labels = c.get("Labels", {})
        short_id = c.get("Id", "")[:12]

        # Dokploy Compose vs Dokploy Swarm vs Standalone
        compose_project = labels.get("com.docker.compose.project")
        compose_service = labels.get("com.docker.compose.service")
        swarm_stack = labels.get("com.docker.stack.namespace")
        dokploy_app = labels.get("dokploy.appName") or labels.get("dokploy.projectName")

        stack_name = swarm_stack or compose_project or dokploy_app or "standalone"
        orchestrator = "swarm" if swarm_stack else ("compose" if compose_project else "docker")
        is_dokploy = bool(dokploy_app or "dokploy" in stack_name.lower())
        traefik_domains = _extract_traefik_domains(labels)

        result.append({
            "id": c.get("Id", "")[:12],
            "full_id": c.get("Id", ""),
            "name": name,
            "stack": stack_name,
            "orchestrator": orchestrator,
            "is_dokploy": is_dokploy,
            "dokploy_app": dokploy_app or "",
            "compose_service": compose_service or "",
            "image": c.get("Image", ""),
            "state": c.get("State", ""),
            "status": c.get("Status", ""),
            "traefik_domains": traefik_domains,
            "created": c.get("Created", 0),
            "ports": c.get("Ports", []),
            "labels": labels,
            "stats": stats_map.get(short_id, {
                "cpu_percent": 0.0,
                "mem_percent": 0.0,
                "mem_usage": "0 B / 0 B",
                "net_rx": "0 B",
                "net_tx": "0 B",
                "block_read": "0 B",
                "block_write": "0 B",
            }),
        })
    return result


def get_dokploy_and_compose_stacks() -> Dict[str, Any]:
    """
    Groups containers and services by Dokploy Application, Compose Project, or Swarm Stack.
    Supports both Docker Compose and Docker Swarm seamlessly.
    """
    containers = list_containers(all_containers=True)
    services = list_swarm_services()

    stacks: Dict[str, Dict[str, Any]] = {}

    # 1. Group Compose / Standalone containers
    for c in containers:
        st_name = c["stack"]
        if st_name not in stacks:
            stacks[st_name] = {
                "name": st_name,
                "orchestrator": c["orchestrator"],
                "is_dokploy": c["is_dokploy"],
                "containers_count": 0,
                "running_count": 0,
                "traefik_domains": [],
                "items": [],
            }
        stacks[st_name]["containers_count"] += 1
        if c["state"] == "running":
            stacks[st_name]["running_count"] += 1
        if c["traefik_domains"]:
            stacks[st_name]["traefik_domains"].extend(c["traefik_domains"])
            stacks[st_name]["traefik_domains"] = list(set(stacks[st_name]["traefik_domains"]))
        stacks[st_name]["items"].append(c)

    # 2. Add Swarm Services if available
    for s in services:
        st_name = s["stack"]
        if st_name not in stacks:
            stacks[st_name] = {
                "name": st_name,
                "orchestrator": "swarm",
                "is_dokploy": s["is_dokploy"],
                "containers_count": 0,
                "running_count": 0,
                "traefik_domains": [],
                "items": [],
            }
        if s["traefik_domains"]:
            stacks[st_name]["traefik_domains"].extend(s["traefik_domains"])
            stacks[st_name]["traefik_domains"] = list(set(stacks[st_name]["traefik_domains"]))
        stacks[st_name]["items"].append(s)

    return {
        "stacks_count": len(stacks),
        "stacks": list(stacks.values()),
    }


def container_action(container_id: str, action: str) -> Dict[str, Any]:
    """Execute action on container: start, stop, restart, kill."""
    if action not in ("start", "stop", "restart", "kill"):
        return {"success": False, "error": "Invalid action"}
    res = docker_cli.request(f"/containers/{container_id}/{action}", method="POST")
    if isinstance(res, dict) and "error" in res:
        return {"success": False, "error": res["error"]}
    return {"success": True, "action": action, "container_id": container_id}


_container_updates_lock = threading.Lock()
_container_updates_cache: Dict[str, Any] = {"ts": 0.0, "items": []}
_CONTAINER_UPDATES_TTL = 600.0


def _inspect_single_container_updates(c: Dict[str, Any]) -> Dict[str, Any]:
    cid = c.get("id", "")
    name = c.get("name", cid)
    image = c.get("image", "")
    docker_bin = shutil.which("docker")
    pending = 0
    if docker_bin and c.get("state") == "running" and re.match(r"^[a-zA-Z0-9_.-]+$", cid):
        script = (
            "if command -v apt-get >/dev/null 2>&1; then "
            "apt-get update -qq >/dev/null 2>&1 && apt-get -s upgrade 2>/dev/null | grep -c '^Inst '; "
            "elif command -v apk >/dev/null 2>&1; then "
            "apk update >/dev/null 2>&1 && apk list -u 2>/dev/null | wc -l; "
            "elif command -v dnf >/dev/null 2>&1; then "
            "dnf check-update -q 2>/dev/null | grep -c '^[a-zA-Z0-9]'; "
            "else echo 0; fi"
        )
        try:
            proc = subprocess.run([docker_bin, "exec", cid, "sh", "-c", script], capture_output=True, text=True, timeout=20)
            out = proc.stdout.strip().splitlines()
            if out and out[-1].strip().isdigit():
                pending = int(out[-1].strip())
        except Exception:
            pass
    return {"id": cid, "name": name, "image": image, "pending_count": pending, "has_update": pending > 0}


def check_container_updates(force: bool = False) -> Dict[str, Any]:
    """Detect pending package updates inside running Docker containers (Postgres, etc.)."""
    now = time.time()
    with _container_updates_lock:
        if not force and _container_updates_cache["items"] and (now - _container_updates_cache["ts"]) < _CONTAINER_UPDATES_TTL:
            items = _container_updates_cache["items"]
            return {"updates": items, "total_with_updates": sum(1 for x in items if x["has_update"])}

    running = [c for c in list_containers(all_containers=False) if c.get("state") == "running"]
    items: List[Dict[str, Any]] = []
    if running:
        with ThreadPoolExecutor(max_workers=min(6, len(running))) as pool:
            items = list(pool.map(_inspect_single_container_updates, running))

    with _container_updates_lock:
        _container_updates_cache["ts"] = now
        _container_updates_cache["items"] = items

    return {"updates": items, "total_with_updates": sum(1 for x in items if x["has_update"])}


def update_container_packages(container_id: str) -> Dict[str, Any]:
    """Update packages inside a running container safely."""
    if not re.match(r"^[a-zA-Z0-9_.-]+$", container_id):
        return {"success": False, "message": "ID de container inválido"}
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return {"success": False, "message": "Docker CLI não encontrado"}

    script = (
        "if command -v apt-get >/dev/null 2>&1; then "
        "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y; "
        "elif command -v apk >/dev/null 2>&1; then "
        "apk update && apk upgrade; "
        "elif command -v dnf >/dev/null 2>&1; then "
        "dnf upgrade -y; "
        "else echo 'Gerenciador interno não suportado'; exit 1; fi"
    )
    try:
        proc = subprocess.run([docker_bin, "exec", container_id, "sh", "-c", script], capture_output=True, text=True, timeout=180)
        with _container_updates_lock:
            _container_updates_cache["ts"] = 0.0
        return {
            "success": proc.returncode == 0,
            "output": (proc.stdout + "\n" + proc.stderr).strip()[-4000:],
        }
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def get_container_logs(container_id: str, tail: int = 100) -> Dict[str, Any]:
    if not re.match(r"^[a-zA-Z0-9_.-]+$", container_id):
        return {"logs": "ID inválido"}
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return {"logs": "Docker CLI não encontrado"}
    try:
        proc = subprocess.run([docker_bin, "logs", "--tail", str(tail), container_id], capture_output=True, text=True, timeout=10)
        return {"logs": (proc.stdout + proc.stderr).strip()}
    except Exception as exc:
        return {"logs": str(exc)}


def get_container_detail(container_id: str) -> Dict[str, Any]:
    """Return full inspection details, mounts, network/ports, and live stats for a container."""
    if not re.match(r"^[a-zA-Z0-9_.-]+$", container_id):
        return {"error": "ID de container inválido"}
    info = docker_cli.request(f"/containers/{container_id}/json")
    if not isinstance(info, dict) or "error" in info:
        return {"error": (info or {}).get("error", "Container não encontrado")}

    state_obj = info.get("State") or {}
    config_obj = info.get("Config") or {}
    host_cfg = info.get("HostConfig") or {}
    net_settings = info.get("NetworkSettings") or {}
    running = bool(state_obj.get("Running"))

    cpu_pct = 0.0
    mem_used = 0
    mem_limit = 0
    mem_pct = 0.0
    net_rx = 0
    net_tx = 0
    blk_read = 0
    blk_write = 0
    pids = 0

    if running:
        stats = docker_cli.request(f"/containers/{container_id}/stats?stream=false")
        if isinstance(stats, dict) and "error" not in stats:
            cpu_stats = stats.get("cpu_stats") or {}
            pre_cpu = stats.get("precpu_stats") or {}
            cpu_delta = (cpu_stats.get("cpu_usage", {}).get("total_usage", 0) or 0) - (
                pre_cpu.get("cpu_usage", {}).get("total_usage", 0) or 0
            )
            sys_delta = (cpu_stats.get("system_cpu_usage", 0) or 0) - (
                pre_cpu.get("system_cpu_usage", 0) or 0
            )
            online_cpus = cpu_stats.get("online_cpus") or len(cpu_stats.get("cpu_usage", {}).get("percpu_usage") or []) or 1
            if sys_delta > 0 and cpu_delta > 0:
                cpu_pct = round((cpu_delta / sys_delta) * online_cpus * 100.0, 2)

            mem_stats = stats.get("memory_stats") or {}
            mem_used = int(mem_stats.get("usage", 0) or 0)
            mem_limit = int(mem_stats.get("limit", 0) or 0)
            if mem_limit > 0:
                mem_pct = round((mem_used / mem_limit) * 100.0, 1)

            for iface_data in (stats.get("networks") or {}).values():
                net_rx += int(iface_data.get("rx_bytes", 0) or 0)
                net_tx += int(iface_data.get("tx_bytes", 0) or 0)

            for blk in (stats.get("blkio_stats") or {}).get("io_service_bytes_recursive") or []:
                op = (blk.get("op") or "").lower()
                val = int(blk.get("value", 0) or 0)
                if op == "read":
                    blk_read += val
                elif op == "write":
                    blk_write += val

            pids = int((stats.get("pids_stats") or {}).get("current", 0) or 0)

    mounts = [
        {
            "type": m.get("Type", "bind"),
            "source": m.get("Source", ""),
            "destination": m.get("Destination", ""),
            "mode": m.get("Mode", ""),
            "rw": bool(m.get("RW", True)),
        }
        for m in (info.get("Mounts") or [])
    ]

    ports = []
    for c_port, bindings in (net_settings.get("Ports") or {}).items():
        if isinstance(bindings, list) and bindings:
            for b in bindings:
                ports.append({
                    "container_port": c_port,
                    "host_ip": b.get("HostIp") or "0.0.0.0",
                    "host_port": b.get("HostPort") or "",
                })
        else:
            ports.append({"container_port": c_port, "host_ip": "-", "host_port": "-"})

    networks = [
        {
            "name": net_name,
            "ip": net_info.get("IPAddress") or "-",
            "gateway": net_info.get("Gateway") or "-",
            "mac": net_info.get("MacAddress") or "-",
        }
        for net_name, net_info in (net_settings.get("Networks") or {}).items()
    ]

    labels = config_obj.get("Labels") or {}
    return {
        "id": info.get("Id", "")[:12],
        "full_id": info.get("Id", ""),
        "name": (info.get("Name") or "").lstrip("/"),
        "image": config_obj.get("Image", ""),
        "state": state_obj.get("Status", "unknown"),
        "running": running,
        "started_at": state_obj.get("StartedAt", ""),
        "restart_count": int(info.get("RestartCount", 0) or 0),
        "restart_policy": (host_cfg.get("RestartPolicy") or {}).get("Name", "no"),
        "traefik_domains": _extract_traefik_domains(labels),
        "metrics": {
            "cpu_percent": cpu_pct,
            "mem_used": mem_used,
            "mem_limit": mem_limit,
            "mem_percent": mem_pct,
            "net_rx": net_rx,
            "net_tx": net_tx,
            "blk_read": blk_read,
            "blk_write": blk_write,
            "pids": pids,
        },
        "mounts": mounts,
        "ports": ports,
        "networks": networks,
    }
