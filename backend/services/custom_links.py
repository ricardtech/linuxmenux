#!/usr/bin/env python3
"""
Linux Menux - Custom Links Service
Stores and manages user-defined web links in /etc/linuxmenux/custom_links.json
with fallback to ~/.config/linuxmenux/custom_links.json.
Provides 1:1 parity with ProxMenux Custom Links architecture.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from typing import Any, Optional, Dict, List, Tuple

_PRIMARY_PATH = "/etc/linuxmenux/custom_links.json"
_FALLBACK_DIR = os.path.expanduser("~/.config/linuxmenux")
_FALLBACK_PATH = os.path.join(_FALLBACK_DIR, "custom_links.json")

_lock = threading.RLock()
_cached_entries: Optional[List[Dict[str, Any]]] = None

_NAME_RE = re.compile(r"^[\w\s._+\-()/:,&]{1,80}$", re.UNICODE)
_URL_RE = re.compile(r"^https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]{1,510}$")
_CATEGORY_RE = re.compile(r"^[\w\s&/,.\-*+()]{1,60}$", re.UNICODE)
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _get_active_path() -> str:
    """Return the writable path for storing custom links."""
    if os.path.exists(_PRIMARY_PATH) or os.access("/etc", os.W_OK):
        return _PRIMARY_PATH
    os.makedirs(_FALLBACK_DIR, exist_ok=True)
    return _FALLBACK_PATH


def _read_from_disk() -> List[Dict[str, Any]]:
    path = _get_active_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            if isinstance(raw, list):
                return [entry for entry in raw if isinstance(entry, dict)]
    except (FileNotFoundError, PermissionError, OSError, ValueError):
        pass

    # Try fallback if primary was missing
    if path != _FALLBACK_PATH and os.path.exists(_FALLBACK_PATH):
        try:
            with open(_FALLBACK_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    return [entry for entry in raw if isinstance(entry, dict)]
        except Exception:
            pass

    return []


def load_all() -> List[Dict[str, Any]]:
    global _cached_entries
    with _lock:
        if _cached_entries is None:
            _cached_entries = _read_from_disk()
        return [dict(e) for e in _cached_entries]


def save_all(entries: List[Dict[str, Any]]) -> None:
    global _cached_entries
    path = _get_active_path()
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    tmp_path = f"{path}.tmp.{os.getpid()}"
    with _lock:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        _cached_entries = [dict(e) for e in entries]


def validate_entry(raw: Any, existing_id: Optional[str] = None) -> Tuple[bool, Any]:
    if not isinstance(raw, dict):
        return False, "Payload deve ser um objeto JSON"

    name = (raw.get("name") or "").strip()
    if not name:
        return False, "Nome é obrigatório"
    if not _NAME_RE.match(name):
        return False, "Nome contém caracteres inválidos ou excede 80 caracteres"

    url = (raw.get("url") or "").strip()
    if not url:
        return False, "URL é obrigatória"
    if not _URL_RE.match(url):
        return False, "URL deve ser válida com protocolo http:// ou https://"

    logo_url = (raw.get("logo_url") or "").strip()
    if logo_url and not _URL_RE.match(logo_url):
        return False, "logo_url deve ser uma URL válida"

    category = (raw.get("category") or "Geral").strip()
    if category and not _CATEGORY_RE.match(category):
        return False, "Categoria inválida"

    entry_id = existing_id or raw.get("id") or str(uuid.uuid4())
    if not _UUID_RE.match(entry_id):
        entry_id = str(uuid.uuid4())

    now = int(time.time())
    return True, {
        "id": entry_id,
        "name": name,
        "url": url,
        "logo_url": logo_url,
        "category": category,
        "created_at": int(raw.get("created_at") or now),
        "updated_at": now,
    }


def create(payload: dict) -> Tuple[bool, Any]:
    ok, entry = validate_entry(payload)
    if not ok:
        return False, entry
    with _lock:
        current = load_all()
        current.append(entry)
        save_all(current)
    return True, entry


def update(link_id: str, payload: dict) -> Tuple[bool, Any]:
    if not _UUID_RE.match(link_id or ""):
        return False, "ID de link inválido"
    with _lock:
        current = load_all()
        for i, existing in enumerate(current):
            if existing.get("id") == link_id:
                merged = dict(existing)
                merged.update(payload)
                merged["id"] = link_id
                merged["created_at"] = existing.get("created_at")
                ok, entry = validate_entry(merged, existing_id=link_id)
                if not ok:
                    return False, entry
                current[i] = entry
                save_all(current)
                return True, entry
        return False, "Link não encontrado"


def delete(link_id: str) -> Tuple[bool, Any]:
    if not _UUID_RE.match(link_id or ""):
        return False, "ID de link inválido"
    with _lock:
        current = load_all()
        remaining = [e for e in current if e.get("id") != link_id]
        if len(remaining) != len(current):
            save_all(remaining)
    return True, {"deleted": link_id}
