"""
Linux Menux Simple & Robust Authentication Manager
Handles password hashing, token generation, profile storage, and login/setup flows.
"""

import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Dict, Any, Optional, Tuple

AUTH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
AUTH_FILE = os.path.join(AUTH_DIR, "auth.json")
SECRET_FILE = os.path.join(AUTH_DIR, "jwt_secret.key")


def _get_secret_key() -> str:
    os.makedirs(AUTH_DIR, exist_ok=True)
    if not os.path.exists(SECRET_FILE):
        key = secrets.token_hex(32)
        with open(SECRET_FILE, "w", encoding="utf-8") as f:
            f.write(key)
        return key
    with open(SECRET_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_auth_config() -> Dict[str, Any]:
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "configured": False,
        "enabled": False,
        "username": "",
        "password_hash": "",
        "salt": "",
    }


def save_auth_config(cfg: Dict[str, Any]):
    os.makedirs(AUTH_DIR, exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hashed, salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    calc = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(calc, hashed)


def generate_jwt(username: str) -> str:
    key = _get_secret_key()
    header = '{"alg":"HS256","typ":"JWT"}'
    payload = json.dumps({
        "sub": username,
        "username": username,
        "exp": int(time.time()) + (86400 * 30),  # 30 days
        "iat": int(time.time()),
        "scope": "admin"
    })
    import base64
    b64_h = base64.urlsafe_b64encode(header.encode("utf-8")).decode("utf-8").rstrip("=")
    b64_p = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8").rstrip("=")
    signing_input = f"{b64_h}.{b64_p}"
    sig = hmac.new(key.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    b64_sig = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return f"{signing_input}.{b64_sig}"


def verify_jwt(token: str) -> Optional[str]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        signing_input = f"{parts[0]}.{parts[1]}"
        key = _get_secret_key()
        sig = hmac.new(key.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        import base64
        calc_sig = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
        if not hmac.compare_digest(calc_sig, parts[2]):
            return None
        # Check payload expiry
        pad = "=" * ((4 - len(parts[1]) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload.get("username")
    except Exception:
        return None
