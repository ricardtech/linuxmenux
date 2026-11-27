"""
Linux Menux Simple & Robust Authentication Manager
Handles password hashing, token generation, profile storage, and login/setup flows.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, Tuple

from core.paths import get_persistent_data_dir

AUTH_DIR = get_persistent_data_dir()
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
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"pbkdf2_sha256${dk.hex()}", salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    if not hashed or not salt:
        return False
    if hashed.startswith("pbkdf2_sha256$"):
        expected = hashed.split("$", 1)[1]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()
        return hmac.compare_digest(dk, expected)
    # Legacy SHA-256 fallback
    calc = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(calc, hashed)


def verify_api_token(raw_token: str) -> Optional[str]:
    """Verify an lmx_* API token against persistent api_tokens.json."""
    if not raw_token or not raw_token.startswith("lmx_"):
        return None
    tokens_file = os.path.join(AUTH_DIR, "api_tokens.json")
    if not os.path.exists(tokens_file):
        return None
    try:
        with open(tokens_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        for item in items:
            if hmac.compare_digest(item.get("token_hash", ""), token_hash):
                return item.get("name", "api-token")
    except Exception:
        pass
    return None


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
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload.get("username")
    except Exception:
        return None


def generate_totp_secret(length: int = 16) -> str:
    raw = secrets.token_bytes(20)
    return base64.b32encode(raw).decode("ascii").rstrip("=")[:length]


def _totp_at(secret: str, counter: int) -> str:
    padded = secret.strip().upper() + "=" * (-len(secret.strip()) % 8)
    key = base64.b32decode(padded, casefold=True)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code_int:06d}"


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    clean = "".join(ch for ch in str(code or "") if ch.isdigit())
    if len(clean) != 6 or not secret:
        return False
    now_step = int(time.time() // 30)
    for offset in range(-window, window + 1):
        try:
            if hmac.compare_digest(_totp_at(secret, now_step + offset), clean):
                return True
        except Exception:
            return False
    return False


def build_otpauth_uri(secret: str, username: str, issuer: str = "Linux Menux Monitor") -> str:
    label = urllib.parse.quote(f"{issuer}:{username}")
    q_issuer = urllib.parse.quote(issuer)
    return f"otpauth://totp/{label}?secret={secret}&issuer={q_issuer}&algorithm=SHA1&digits=6&period=30"


def send_telegram_2fa_code(bot_token: str, chat_id: str, code: str) -> Tuple[bool, str]:
    token = str(bot_token or "").strip()
    cid = str(chat_id or "").strip()
    if not token or not cid:
        return False, "Bot Token e Chat ID do Telegram são obrigatórios."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": cid,
        "text": f"🔐 *Linux Menux - Monitor*\nSeu código de verificação 2FA é: `{code}`\n\nVálido por 5 minutos.",
        "parse_mode": "Markdown",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return True, "Código enviado para o Telegram."
            return False, data.get("description") or "Falha na API do Telegram."
    except Exception as exc:
        return False, f"Erro ao enviar no Telegram: {exc}"
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
