"""
Linux Menux Main Application Server
Combines FastAPI REST endpoints, WebSockets, Docker Compose/Swarm, Traefik,
and static frontend assets.
"""

import os
import platform
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles

from core.distro import detect_system_info
from services.system_metrics import collect_all_metrics, get_disk_mounts
from services.docker_swarm import (
    get_docker_overview,
    list_swarm_services,
    list_containers,
    get_dokploy_and_compose_stacks,
    container_action,
)
from services.traefik_monitor import get_traefik_info
from services.firewall_monitor import inspect_firewall
from services.pkg_manager import (
    check_updates,
    check_reboot_required,
    apply_updates_async,
    get_update_status,
    execute_system_reboot,
)
from core.auth import (
    load_auth_config,
    save_auth_config,
    hash_password,
    verify_password,
    generate_jwt,
    verify_jwt,
)
from api.terminal import issue_ticket, consume_ticket, handle_terminal_session

app = FastAPI(title="Linux Menux Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health & Platform Compatibility ───────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Linux Menux"}


@app.get("/api/platform")
def get_platform():
    # Return pve for maximum frontend widget compatibility
    return {"product": "pve", "app": "linuxmenux"}


@app.get("/api/monitor-links")
def get_monitor_links():
    return {
        "self": {"name": "Linux Menux", "product": "pve"},
        "links": [
            {
                "key": "local",
                "name": "Linux Menux (Local)",
                "product": "pve",
                "group": "standalone",
                "url": "http://localhost:8008",
                "status": "online",
                "manual": False,
                "local": True,
                "hidden": False,
                "custom_url": False,
            }
        ],
    }


@app.post("/api/monitor-links")
def post_monitor_links():
    return {"success": True}


# ─── Auth Endpoints ────────────────────────────────────────────────────────

@app.get("/api/auth/status")
def auth_status(request: Request):
    auth_cfg = load_auth_config()
    is_configured = auth_cfg.get("configured", False)
    is_enabled = auth_cfg.get("enabled", False)

    # Check authorization header
    auth_header = request.headers.get("Authorization", "")
    authenticated = False
    username = auth_cfg.get("username", "admin")

    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        verified = verify_jwt(token)
        if verified:
            authenticated = True
            username = verified

    if not is_configured:
        # Before initial setup: open by default
        return {
            "auth_enabled": False,
            "auth_configured": False,
            "authenticated": True,
            "username": "admin",
        }

    return {
        "auth_enabled": is_enabled,
        "auth_configured": is_configured,
        "authenticated": authenticated if is_enabled else True,
        "username": username,
    }


@app.post("/api/auth/setup")
async def auth_setup(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    if not username or not password:
        raise HTTPException(status_code=400, detail="Usuário e senha são obrigatórios")

    hashed, salt = hash_password(password)
    cfg = {
        "configured": True,
        "enabled": True,
        "username": username,
        "password_hash": hashed,
        "salt": salt,
        "display_name": username,
        "updated_at": datetime.now().isoformat(),
    }
    save_auth_config(cfg)
    token = generate_jwt(username)

    return {
        "success": True,
        "token": token,
        "message": "Autenticação configurada com sucesso",
    }


@app.post("/api/auth/login")
async def auth_login(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    cfg = load_auth_config()
    if not cfg.get("configured"):
        token = generate_jwt(username or "admin")
        return {"success": True, "token": token, "username": username or "admin"}

    if username == cfg.get("username") and verify_password(password, cfg.get("password_hash", ""), cfg.get("salt", "")):
        token = generate_jwt(username)
        return {"success": True, "token": token, "username": username}

    raise HTTPException(status_code=401, detail="Nome de usuário ou senha incorretos")


@app.post("/api/auth/skip")
def auth_skip():
    cfg = load_auth_config()
    cfg["configured"] = True
    cfg["enabled"] = False
    save_auth_config(cfg)
    return {"success": True, "auth_declined": True}


@app.get("/api/auth/profile")
def get_auth_profile():
    cfg = load_auth_config()
    return {
        "username": cfg.get("username", "AlaxRicard"),
        "display_name": cfg.get("display_name", cfg.get("username", "AlaxRicard")),
        "avatar_mtime": int(time.time()),
        "totp_enabled": False,
    }


@app.put("/api/auth/profile")
async def update_auth_profile(request: Request):
    try:
        body = await request.json()
        display_name = body.get("display_name")
        if display_name:
            cfg = load_auth_config()
            cfg["display_name"] = display_name
            save_auth_config(cfg)
    except Exception:
        pass
    return {"success": True}


@app.post("/api/auth/profile/avatar")
def upload_avatar():
    return {"success": True}


@app.get("/api/auth/profile/avatar")
def get_avatar():
    svg_avatar = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>"""
    return Response(content=svg_avatar, media_type="image/svg+xml")


@app.get("/api/auth/api-tokens")
def get_api_tokens():
    return []


# ─── Apps & Launchers ──────────────────────────────────────────────────────

@app.get("/api/apps/custom-links")
def get_custom_links():
    return []


@app.post("/api/apps/custom-links")
def create_custom_link():
    return {"success": True, "id": "1"}


@app.delete("/api/apps/custom-links/{link_id}")
def delete_custom_link(link_id: str):
    return {"success": True}


@app.get("/api/apps/categories")
def get_apps_categories():
    return ["Geral", "Containers", "DevOps", "Monitoramento", "Web", "Banco de Dados"]


@app.get("/api/apps/catalog")
def get_apps_catalog():
    return []


@app.get("/api/apps/github-token")
def get_github_token():
    return {"configured": False}


# ─── System Metrics & Information ──────────────────────────────────────────

@app.get("/api/system-info")
def get_system_info_header():
    metrics = collect_all_metrics()
    info = detect_system_info()
    uptime_sec = int(metrics["uptime_seconds"])
    hours = uptime_sec // 3600
    minutes = (uptime_sec % 3600) // 60
    return {
        "hostname": info["hostname"],
        "uptime_seconds": uptime_sec,
        "uptime": f"{hours}h {minutes}m",
        "health": {
            "status": "healthy",
            "issues_count": 0,
            "critical_count": 0,
            "warning_count": 0,
            "summary": "Todos os sistemas operacionais",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health/full")
def get_health_full():
    now = datetime.now().isoformat()
    return {
        "health": {
            "overall": "OK",
            "summary": "Todos os sistemas operacionais",
            "details": {},
            "timestamp": now,
        },
        "active_errors": [],
        "dismissed": [],
        "custom_suppressions": [],
        "timestamp": now,
    }


@app.get("/api/system")
def get_system():
    metrics = collect_all_metrics()
    info = detect_system_info()
    uptime_sec = int(metrics["uptime_seconds"])
    hours = uptime_sec // 3600
    minutes = (uptime_sec % 3600) // 60
    return {
        "hostname": info["hostname"],
        "node_id": info["hostname"],
        "serverName": f"Linux Menux ({info['distro_name']})",
        "uptime": f"{hours}h {minutes}m",
        "cpu_usage": metrics["cpu"]["load_percent"],
        "memory_usage": metrics["memory"]["ram_percent"],
        "info": info,
        "metrics": metrics,
    }


@app.get("/api/hardware")
@app.get("/api/hardware/live")
def get_hardware():
    metrics = collect_all_metrics()
    info = detect_system_info()
    return {
        "hostname": info["hostname"],
        "cpu": {
            "model": platform.processor() or "Generic x86_64 CPU",
            "cores": metrics["cpu"]["cores"],
            "usage": metrics["cpu"]["load_percent"],
            "load_1m": metrics["cpu"]["load_1m"],
            "load_5m": metrics["cpu"]["load_5m"],
            "load_15m": metrics["cpu"]["load_15m"],
        },
        "memory": {
            "total": metrics["memory"]["ram_total"],
            "used": metrics["memory"]["ram_used"],
            "free": metrics["memory"]["ram_available"],
            "percent": metrics["memory"]["ram_percent"],
        },
        "disks": metrics["disks"],
        "temperatures": [],
    }


@app.get("/api/storage/summary")
def get_storage():
    mounts = get_disk_mounts()
    return {
        "storages": mounts,
        "total_disks": len(mounts),
    }


@app.get("/api/proxmox-storage")
def get_proxmox_storage_fallback():
    mounts = get_disk_mounts()
    storages = []
    for m in mounts:
        storages.append({
            "storage": m.get("mountpoint", "root"),
            "type": m.get("type", "ext4"),
            "status": "active",
            "total": m.get("total_bytes", 1000000000),
            "used": m.get("used_bytes", 100000000),
            "avail": m.get("available_bytes", 900000000),
            "shared": 0,
            "content": "containers,data",
        })
    return storages if storages else [{
        "storage": "rootfs",
        "type": "dir",
        "status": "active",
        "total": 50000000000,
        "used": 15000000000,
        "avail": 35000000000,
        "shared": 0,
        "content": "containers,data",
    }]


@app.get("/api/network/summary")
def get_network():
    return {
        "interfaces": ["eth0", "docker0"],
        "status": "online",
    }


@app.get("/api/proxmenux/update-status")
def get_app_update_status():
    return {
        "success": True,
        "update_available": {
            "stable": False,
            "stable_version": "1.0.0",
            "beta": False,
            "beta_version": "1.0.0",
        },
    }


# ─── Docker, Compose & Swarm Endpoints ─────────────────────────────────────

@app.get("/api/docker/overview")
def docker_overview():
    return get_docker_overview()


@app.get("/api/docker/stacks")
def docker_stacks():
    """Returns grouped Dokploy Compose Projects and Swarm Stacks."""
    return get_dokploy_and_compose_stacks()


@app.get("/api/docker/services")
def docker_services():
    return {"services": list_swarm_services()}


@app.get("/api/docker/containers")
def docker_containers(all: bool = True):
    return {"containers": list_containers(all_containers=all)}


@app.post("/api/docker/containers/{container_id}/{action}")
def run_container_action(container_id: str, action: str):
    return container_action(container_id, action)


# Compatibility bridge: Maps Docker Containers to VM shape for legacy components
@app.get("/api/vms")
def vms_compatibility():
    containers = list_containers(all_containers=True)
    vms = []
    for c in containers:
        vms.append({
            "vmid": c["id"],
            "name": c["name"],
            "status": "running" if c["state"] == "running" else "stopped",
            "type": f"Docker ({c['orchestrator'].upper()})",
            "stack": c["stack"],
            "cpu": 0,
            "mem": 0,
            "maxmem": 0,
            "uptime": c["status"],
            "image": c["image"],
            "is_dokploy": c.get("is_dokploy", False),
            "traefik_domains": c.get("traefik_domains", []),
            "ports": [f"{p.get('PublicPort', '')}->{p.get('PrivatePort', '')}" for p in c.get("ports", []) if "PublicPort" in p],
        })
    return vms


@app.get("/api/vms/modal-cache-all")
def vms_modal_cache_all():
    return {"cache": {}}


@app.get("/api/lxc-update-jobs")
def lxc_update_jobs():
    return {"jobs": []}


# ─── Fallback Endpoints for UI Safety ─────────────────────────────────────

@app.get("/api/backups")
def get_backups():
    return {"backups": []}


@app.get("/api/backup-storages")
def get_backup_storages():
    return {"storages": []}


@app.get("/api/events")
def get_events():
    return {"events": []}


@app.get("/api/notifications")
def get_notifications():
    return []


@app.get("/api/notifications/settings")
def get_notifications_settings():
    return {"channels": []}


@app.get("/api/notifications/history")
def get_notifications_history():
    return {"history": []}


@app.get("/api/notifications/status")
def get_notifications_status():
    return {"enabled": False}


@app.get("/api/audit/changes")
def get_audit_changes():
    return {"changes": []}


@app.get("/api/audit/inventory")
def get_audit_inventory():
    return {"inventory": []}


@app.get("/api/audit/status")
def get_audit_status():
    return {"status": "ok"}


@app.get("/api/audit/profiles")
def get_audit_profiles():
    return {"profiles": []}


@app.get("/api/audit/policy")
def get_audit_policy():
    return {"policy": {}}


@app.get("/api/audit/lynis-readiness")
def get_audit_lynis():
    return {"installed": False}


@app.get("/api/security/firewall/status")
def get_sec_firewall_status():
    return {"enabled": True, "status": "active"}


@app.get("/api/security/fail2ban/activity")
def get_sec_fail2ban_act():
    return {"jails": []}


@app.get("/api/security/fail2ban/details")
def get_sec_fail2ban_det():
    return {"jails": []}


@app.get("/api/security/tools")
def get_sec_tools():
    return {"tools": []}


@app.get("/api/ssl/status")
def get_ssl_status():
    return {"valid": True}


@app.get("/api/host-update-jobs")
def get_host_update_jobs():
    return {"jobs": []}


@app.get("/api/lxc-updates/detection")
def get_lxc_updates_detection():
    return {"updates": []}


@app.get("/api/managed-installs")
def get_managed_installs():
    return {"installs": []}


@app.get("/api/proxmenux/installed-tools")
def get_proxmenux_tools():
    return {"tools": ["docker", "fastapi"]}


# ─── Traefik & Firewall ───────────────────────────────────────────────────

@app.get("/api/traefik")
def traefik():
    return get_traefik_info()


@app.get("/api/firewall")
def firewall():
    return inspect_firewall()


# ─── Updates & Reboot ─────────────────────────────────────────────────────

@app.get("/api/updates/check")
def updates_check():
    return {
        "updates": check_updates(),
        "reboot": check_reboot_required(),
    }


@app.post("/api/updates/apply")
def updates_apply():
    return apply_updates_async()


@app.get("/api/updates/status")
def updates_status():
    return get_update_status()


@app.post("/api/system/reboot")
def trigger_reboot():
    return execute_system_reboot()


# ─── Terminal WebSockets ──────────────────────────────────────────────────

@app.post("/api/terminal/ticket")
def request_terminal_ticket():
    ticket = issue_ticket()
    return {"ticket": ticket, "expires_in": 5}


@app.websocket("/ws/terminal")
async def websocket_terminal_endpoint(websocket: WebSocket, ticket: str = Query(None)):
    if not ticket or not consume_ticket(ticket):
        await websocket.close(code=4001, reason="Invalid or expired ticket")
        return

    await websocket.accept()
    await handle_terminal_session(websocket)


# Mount static frontend if available
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8008"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
