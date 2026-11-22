"""
LinuxMenux Main Application Server
Combines FastAPI REST endpoints, WebSockets, and static frontend assets.
"""

import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from core.distro import detect_system_info
from services.system_metrics import collect_all_metrics
from services.docker_swarm import get_docker_overview, list_swarm_services, list_containers, container_action
from services.traefik_monitor import get_traefik_info
from services.firewall_monitor import inspect_firewall
from services.pkg_manager import check_updates, check_reboot_required, apply_updates_async, get_update_status, execute_system_reboot
from api.terminal import issue_ticket, consume_ticket, handle_terminal_session

app = FastAPI(title="LinuxMenux Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "LinuxMenux"}


@app.get("/api/system")
def get_system():
    return {
        "info": detect_system_info(),
        "metrics": collect_all_metrics(),
    }


@app.get("/api/docker/overview")
def docker_overview():
    return get_docker_overview()


@app.get("/api/docker/services")
def docker_services():
    return {"services": list_swarm_services()}


@app.get("/api/docker/containers")
def docker_containers(all: bool = True):
    return {"containers": list_containers(all_containers=all)}


@app.post("/api/docker/containers/{container_id}/{action}")
def run_container_action(container_id: str, action: str):
    return container_action(container_id, action)


@app.get("/api/traefik")
def traefik():
    return get_traefik_info()


@app.get("/api/firewall")
def firewall():
    return inspect_firewall()


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
