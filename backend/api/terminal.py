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
import select
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
    master_fd, slave_fd = pty.openpty()
    shell = os.environ.get("SHELL", "/bin/bash")

    # Set non-blocking on master_fd
    flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
    fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    proc = await asyncio.create_subprocess_exec(
        shell,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=os.path.expanduser("~"),
        preexec_fn=os.setsid,
        env=dict(os.environ, TERM="xterm-256color")
    )
    os.close(slave_fd)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def sync_read():
        while not stop_event.is_set():
            r, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in r:
                try:
                    data = os.read(master_fd, 4096)
                    if not data:  # EOF
                        return None
                    return data.decode("utf-8", errors="replace")
                except OSError:
                    return None
            else:
                continue
        return None

    async def pty_to_ws():
        try:
            while not stop_event.is_set():
                chunk = await loop.run_in_executor(None, sync_read)
                if chunk is None:
                    break
                await websocket.send_text(chunk)
        except Exception:
            pass
        finally:
            stop_event.set()

    async def ws_to_pty():
        try:
            while not stop_event.is_set():
                msg = await websocket.receive_text()
                if msg.startswith('{"type":"resize"') or msg.startswith('{"resize":') or '"resize"' in msg:
                    try:
                        import json
                        payload = json.loads(msg)
                        rows = payload.get("rows")
                        cols = payload.get("cols")
                        if rows and cols:
                            _set_pty_size(master_fd, int(rows), int(cols))
                    except Exception:
                        pass
                elif msg == '{"type":"ping"}' or msg == '{"type": "ping"}':
                    await websocket.send_text('{"type":"pong"}')
                else:
                    os.write(master_fd, msg.encode("utf-8"))
        except Exception:
            pass
        finally:
            stop_event.set()

    task1 = asyncio.create_task(pty_to_ws())
    task2 = asyncio.create_task(ws_to_pty())

    await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
    stop_event.set()
    task1.cancel()
    task2.cancel()

    try:
        proc.terminate()
        await proc.wait()
    except Exception:
        pass
    try:
        os.close(master_fd)
    except OSError:
        pass


def _set_pty_size(fd: int, rows: int, cols: int):
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
