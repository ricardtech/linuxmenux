"""
LinuxMenux Docker Engine & Swarm Monitor
Communicates natively with /var/run/docker.sock to inspect Docker Swarm clusters,
Dokploy Stacks, Services, and Containers.
"""

import http.client
import json
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
    """Lightweight Docker Engine & Swarm API client using the local Unix domain socket."""
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


def get_docker_overview() -> Dict[str, Any]:
    """Returns general Docker Engine and Swarm state."""
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

        services.append({
            "id": svc.get("ID"),
            "name": spec.get("Name"),
            "stack": stack,
            "image": spec.get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image", "").split("@")[0],
            "replicas_target": replicas,
            "created_at": svc.get("CreatedAt"),
            "updated_at": svc.get("UpdatedAt"),
            "labels": labels,
        })
    return services


def list_containers(all_containers: bool = True) -> List[Dict[str, Any]]:
    """List all containers on the host with status, image, and ports."""
    path = f"/containers/json?all={'true' if all_containers else 'false'}"
    raw = docker_cli.request(path)
    if not isinstance(raw, list):
        return []

    result = []
    for c in raw:
        names = [n.lstrip("/") for n in c.get("Names", [])]
        name = names[0] if names else c.get("Id", "")[:12]
        labels = c.get("Labels", {})
        stack = labels.get("com.docker.stack.namespace", labels.get("com.docker.compose.project", "standalone"))

        result.append({
            "id": c.get("Id", "")[:12],
            "full_id": c.get("Id", ""),
            "name": name,
            "stack": stack,
            "image": c.get("Image", ""),
            "state": c.get("State", ""),
            "status": c.get("Status", ""),
            "created": c.get("Created", 0),
            "ports": c.get("Ports", []),
        })
    return result


def container_action(container_id: str, action: str) -> Dict[str, Any]:
    """Execute action on container: start, stop, restart, kill."""
    if action not in ("start", "stop", "restart", "kill"):
        return {"success": False, "error": "Invalid action"}
    res = docker_cli.request(f"/containers/{container_id}/{action}", method="POST")
    if isinstance(res, dict) and "error" in res:
        return {"success": False, "error": res["error"]}
    return {"success": True, "action": action, "container_id": container_id}
