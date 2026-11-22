"""
LinuxMenux Traefik Inspector
Monitors Traefik proxy routes, entrypoints, and SSL/TLS certificates when used with Dokploy/Docker.
"""

import http.client
import json
import socket
from typing import Dict, Any, List, Optional
from services.docker_swarm import docker_cli


def get_traefik_info() -> Dict[str, Any]:
    """
    Inspects Traefik either by querying its Docker container labels/ports
    or by querying its local dashboard/API endpoint (typically 8080).
    """
    result: Dict[str, Any] = {
        "detected": False,
        "container_status": None,
        "routers_count": 0,
        "entrypoints": [],
        "routers": [],
    }

    # 1. Search for Traefik container
    containers = docker_cli.request("/containers/json?all=true")
    traefik_container = None
    if isinstance(containers, list):
        for c in containers:
            names = " ".join(c.get("Names", [])).lower()
            image = c.get("Image", "").lower()
            if "traefik" in names or "traefik" in image:
                traefik_container = c
                break

    if traefik_container:
        result["detected"] = True
        result["container_status"] = traefik_container.get("Status")
        result["container_id"] = traefik_container.get("Id", "")[:12]

    # 2. Try to query local Traefik API if enabled
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=2)
        conn.request("GET", "/api/http/routers")
        res = conn.getresponse()
        if res.status == 200:
            routers = json.loads(res.read().decode("utf-8"))
            result["routers_count"] = len(routers)
            for r in routers[:30]:
                result["routers"].append({
                    "name": r.get("name"),
                    "rule": r.get("rule"),
                    "service": r.get("service"),
                    "status": r.get("status"),
                    "tls": bool(r.get("tls")),
                })
        conn.close()
    except Exception:
        pass

    return result
