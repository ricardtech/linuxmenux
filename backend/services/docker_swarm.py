"""
Linux Menux Docker Engine, Compose & Swarm Monitor
Natively communicates with /var/run/docker.sock to inspect Docker Swarm clusters,
Dokploy Stacks, Compose Projects, and Containers.
"""

import http.client
import json
import re
import socket
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
        self.socket_path = socket_path

    def request(self, path: str, method: str = "GET", body: Optional[bytes] = None) -> Any:
        try:
            conn = UnixSocketHTTPConnection(self.socket_path, timeout=5)
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


def list_containers(all_containers: bool = True) -> List[Dict[str, Any]]:
    """List all containers on the host with status, Dokploy metadata, and Traefik domains."""
    path = f"/containers/json?all={'true' if all_containers else 'false'}"
    raw = docker_cli.request(path)
    if not isinstance(raw, list):
        return []

    result = []
    for c in raw:
        names = [n.lstrip("/") for n in c.get("Names", [])]
        name = names[0] if names else c.get("Id", "")[:12]
        labels = c.get("Labels", {})

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
