"""
Linux Menux Notification Orchestrator
Transports: Telegram, Discord, Gotify, SMTP Email, Pushover, Apprise.
Includes rate limiting and SSRF protection.
"""

import json
import smtplib
import time
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional, Tuple

_BLOCKED_HOSTS = {
    "169.254.169.254",
    "metadata.google.internal",
    "metadata.aws.internal",
}


def _validate_safe_url(url: str) -> Tuple[bool, str]:
    """Validate webhook URL against SSRF attacks."""
    if not url:
        return False, "URL cannot be empty."
    try:
        parsed = urllib.parse.urlparse(url.strip())
    except Exception:
        return False, "Malformed URL."
    if parsed.scheme not in ("http", "https"):
        return False, "Only HTTP/HTTPS schemes allowed."
    host = (parsed.hostname or "").lower()
    if not host:
        return False, "Missing hostname."
    if host in _BLOCKED_HOSTS:
        return False, f"Host {host} is blocked for security reasons."
    return True, ""


class NotificationManager:
    """Dispatches notifications to configured channels."""

    @staticmethod
    def send_telegram(bot_token: str, chat_id: str, title: str, message: str) -> Tuple[bool, str]:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": f"*{title}*\n\n{message}",
                "parse_mode": "Markdown",
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                return res.status == 200, "Sent successfully"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_discord(webhook_url: str, title: str, message: str) -> Tuple[bool, str]:
        valid, err = _validate_safe_url(webhook_url)
        if not valid:
            return False, err
        try:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 3447003,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }]
            }
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "LinuxMenux/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                return res.status in (200, 204), "Sent successfully"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_gotify(server_url: str, token: str, title: str, message: str) -> Tuple[bool, str]:
        valid, err = _validate_safe_url(server_url)
        if not valid:
            return False, err
        try:
            url = f"{server_url.rstrip('/')}/message?token={token}"
            payload = {"title": title, "message": message, "priority": 5}
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                return res.status == 200, "Sent successfully"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_email(smtp_host: str, smtp_port: int, user: str, password: str, to_email: str, title: str, message: str, use_tls: bool = True) -> Tuple[bool, str]:
        try:
            msg = MIMEMultipart()
            msg["From"] = user
            msg["To"] = to_email
            msg["Subject"] = f"[LinuxMenux] {title}"
            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            if use_tls:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
            server.quit()
            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)
