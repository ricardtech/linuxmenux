"""
Linux Menux Terminal WebSocket Handler
Provides a secure PTY terminal session connected to xterm.js via WebSockets.
Protected by short-lived (5-second TTL) single-use tickets.
"""

import asyncio
import fcntl
import os
import pty
import secrets
import struct
import termios
import time
from typing import Dict, Optional

# Tickets cache with 5s TTL
_terminal_tickets: Dict[str, float] = {}
_TICKET_TTL = 5.0


def issue_ticket() -> str:
    """Generate a single-use ticket valid for 5 seconds."""
    now = time.time()
    # Prune expired
    for k in list(_terminal_tickets.keys()):
        if now - _terminal_tickets[k] > _TICKET_TTL:
            _terminal_tickets.pop(k, None)

    ticket = secrets.token_urlsafe(32)
    _terminal_tickets[ticket] = now
    return ticket


def consume_ticket(ticket: str) -> bool:
    """Atomically consume ticket. Return True if valid and not expired."""
    if not ticket or ticket not in _terminal_tickets:
        return False
    ts = _terminal_tickets.pop(ticket, None)
    if ts is None:
        return False
    return (time.time() - ts) <= _TICKET_TTL


async def handle_terminal_session(websocket):
    """Bridge WebSocket with a local bash PTY session."""
    # Spawn PTY
    master_fd, slave_fd = pty.openpty()
    shell = os.environ.get("SHELL", "/bin/bash")

    proc = await asyncio.create_subprocess_exec(
        shell,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        preexec_fn=os.setsid,
    )
    os.close(slave_fd)

    # Set non-blocking on master_fd
    flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
    fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    loop = asyncio.get_running_loop()

    async def pty_to_ws():
        try:
            while True:
                data = await loop.run_in_executor(None, lambda: _read_pty(master_fd))
                if not data:
                    break
                await websocket.send_text(data)
        except Exception:
            pass

    async def ws_to_pty():
        try:
            while True:
                msg = await websocket.receive_text()
                # Check for resize message: e.g. {"resize": [rows, cols]}
                if msg.startswith('{"resize":'):
                    try:
                        import json
                        payload = json.loads(msg)
                        rows, cols = payload["resize"]
                        _set_pty_size(master_fd, rows, cols)
                    except Exception:
                        pass
                else:
                    os.write(master_fd, msg.encode("utf-8"))
        except Exception:
            pass

    task1 = asyncio.create_task(pty_to_ws())
    task2 = asyncio.create_task(ws_to_pty())

    done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()

    try:
        proc.terminate()
        os.close(master_fd)
    except OSError:
        pass


def _read_pty(fd: int) -> Optional[str]:
    try:
        data = os.read(fd, 4096)
        return data.decode("utf-8", errors="replace")
    except (OSError, BlockingIOError):
        time.sleep(0.02)
        return ""


def _set_pty_size(fd: int, rows: int, cols: int):
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
