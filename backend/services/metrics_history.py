"""
Linux Menux Persistent Metrics History & Update Cache
Samples real CPU, Load, Memory, and Network RX/TX counters into SQLite
so 1h / 24h / 7d / 30d / 1y charts and totals reflect real host history.
"""

import json
import os
import shutil
import sqlite3
import subprocess
import threading
import time
from typing import Any, Dict, List, Optional

from core.paths import get_persistent_data_dir
from services.host_inspector import get_real_cpu_metrics, get_real_memory_metrics, get_real_temperature
from services.pkg_manager import check_reboot_required, check_updates

DATA_DIR = get_persistent_data_dir()
DB_PATH = os.path.join(DATA_DIR, "metrics_history.db")

_db_lock = threading.Lock()
_collector_started = False
_prev_net_counters: Optional[Dict[str, int]] = None

_updates_cache_lock = threading.Lock()
_updates_cache: Dict[str, Any] = {
    "timestamp": 0.0,
    "updates": None,
    "reboot": None,
}
_UPDATES_TTL_SECONDS = 300.0


def _get_conn() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_metrics_db() -> None:
    with _db_lock:
        conn = _get_conn()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_samples (
                    ts INTEGER PRIMARY KEY,
                    cpu_percent REAL NOT NULL,
                    load_1m REAL NOT NULL,
                    mem_used INTEGER NOT NULL,
                    mem_total INTEGER NOT NULL,
                    net_rx_delta INTEGER NOT NULL,
                    net_tx_delta INTEGER NOT NULL,
                    temp_c REAL NOT NULL DEFAULT 0.0
                )
                """
            )
            cols = {r[1] for r in conn.execute("PRAGMA table_info(system_samples)").fetchall()}
            if "temp_c" not in cols:
                conn.execute("ALTER TABLE system_samples ADD COLUMN temp_c REAL NOT NULL DEFAULT 0.0")
            conn.commit()
        finally:
            conn.close()


def _read_proc_net_totals() -> Dict[str, int]:
    rx_total = 0
    tx_total = 0
    try:
        with open("/proc/net/dev", "r", encoding="utf-8") as f:
            for line in f.readlines()[2:]:
                if ":" not in line:
                    continue
                iface, rest = line.split(":", 1)
                iface = iface.strip()
                if iface == "lo" or iface.startswith(("docker", "veth", "br-")):
                    continue
                parts = rest.split()
                if len(parts) >= 9:
                    rx_total += int(parts[0])
                    tx_total += int(parts[8])
    except OSError:
        pass
    return {"rx": rx_total, "tx": tx_total}


def record_sample() -> None:
    global _prev_net_counters
    now = int(time.time())
    cpu = get_real_cpu_metrics()
    mem = get_real_memory_metrics()
    temp = get_real_temperature()
    temp_c = float(temp.get("current", 0.0) or 0.0)
    net_now = _read_proc_net_totals()

    rx_delta = 0
    tx_delta = 0
    if _prev_net_counters is not None:
        rx_delta = max(0, net_now["rx"] - _prev_net_counters["rx"])
        tx_delta = max(0, net_now["tx"] - _prev_net_counters["tx"])
    _prev_net_counters = net_now

    with _db_lock:
        conn = _get_conn()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO system_samples
                (ts, cpu_percent, load_1m, mem_used, mem_total, net_rx_delta, net_tx_delta, temp_c)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    now,
                    float(cpu.get("usage_percent", 0.0)),
                    float(cpu.get("load_1m", 0.0)),
                    int(mem.get("used", 0)),
                    int(mem.get("total", 0)),
                    int(rx_delta),
                    int(tx_delta),
                    temp_c,
                ),
            )
            cutoff = now - 366 * 86400
            conn.execute("DELETE FROM system_samples WHERE ts < ?", (cutoff,))
            conn.commit()
        finally:
            conn.close()


def start_metrics_collector() -> None:
    global _collector_started
    if _collector_started:
        return
    _collector_started = True
    init_metrics_db()
    try:
        record_sample()
    except Exception:
        pass

    def _loop() -> None:
        while True:
            time.sleep(10)
            try:
                record_sample()
            except Exception:
                pass

    threading.Thread(target=_loop, daemon=True, name="metrics-collector").start()


def _query_vnstat_network(timeframe: str, now: int, window_sec: int) -> Optional[Dict[str, Any]]:
    """Query real historical network traffic from vnstat --json when available."""
    vnstat_bin = shutil.which("vnstat")
    if not vnstat_bin:
        return None
    mode_map = {
        "hour": ("f", "fiveminute"),
        "day": ("f", "fiveminute"),
        "week": ("h", "hour"),
        "month": ("d", "day"),
        "year": ("m", "month"),
    }
    flag, key = mode_map.get(timeframe, ("f", "fiveminute"))
    try:
        proc = subprocess.run([vnstat_bin, "--json", flag], capture_output=True, text=True, timeout=5)
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        parsed = json.loads(proc.stdout)
        since_ts = now - window_sec
        buckets: Dict[int, Dict[str, int]] = {}
        for iface in parsed.get("interfaces", []):
            name = iface.get("name", "")
            if not name or name == "lo" or name.startswith(("docker", "veth", "br-", "tailscale")):
                continue
            for entry in (iface.get("traffic") or {}).get(key, []):
                ts = int(entry.get("timestamp") or 0)
                if ts <= 0 or ts < since_ts:
                    continue
                if ts not in buckets:
                    buckets[ts] = {"rx": 0, "tx": 0}
                buckets[ts]["rx"] += int(entry.get("rx") or 0)
                buckets[ts]["tx"] += int(entry.get("tx") or 0)

        if not buckets:
            return None
        sorted_ts = sorted(buckets.keys())
        pts = [{"time": ts * 1000, "rx": buckets[ts]["rx"], "tx": buckets[ts]["tx"]} for ts in sorted_ts]
        return {
            "points": pts,
            "total_rx": sum(p["rx"] for p in pts),
            "total_tx": sum(p["tx"] for p in pts),
        }
    except Exception:
        return None


def query_metrics(timeframe: str = "day") -> Dict[str, Any]:
    """Query aggregated historical metrics from SQLite for hour/day/week/month/year."""
    init_metrics_db()
    now = int(time.time())
    tf_map = {
        "hour": (3600, 60),        # 1h, 1-min buckets
        "day": (86400, 1800),      # 24h, 30-min buckets
        "week": (7 * 86400, 14400),  # 7d, 4-hour buckets
        "month": (30 * 86400, 86400),  # 30d, 1-day buckets
        "year": (365 * 86400, 7 * 86400),  # 1y, 7-day buckets
    }
    window_sec, bucket_sec = tf_map.get(timeframe, (86400, 1800))
    since_ts = now - window_sec

    with _db_lock:
        conn = _get_conn()
        try:
            def _fetch_buckets(b_sec: int):
                return conn.execute(
                    """
                    SELECT
                        (ts / ?) * ? AS bucket_ts,
                        AVG(cpu_percent) AS avg_cpu,
                        MAX(cpu_percent) AS max_cpu,
                        MIN(cpu_percent) AS min_cpu,
                        AVG(load_1m) AS avg_load,
                        AVG(mem_used) AS avg_mem,
                        MAX(mem_used) AS max_mem,
                        MIN(mem_used) AS min_mem,
                        MAX(mem_total) AS mem_total,
                        SUM(net_rx_delta) AS sum_rx,
                        SUM(net_tx_delta) AS sum_tx
                    FROM system_samples
                    WHERE ts >= ?
                    GROUP BY bucket_ts
                    ORDER BY bucket_ts ASC
                    """,
                    (b_sec, b_sec, since_ts),
                ).fetchall()

            rows = _fetch_buckets(bucket_sec)
            if len(rows) < 6 and bucket_sec > 60:
                rows = _fetch_buckets(60)
        finally:
            conn.close()

    if not rows:
        record_sample()
        return query_metrics(timeframe)

    points: List[Dict[str, Any]] = []
    cpu_avgs: List[float] = []
    cpu_maxs: List[float] = []
    cpu_mins: List[float] = []
    mem_avgs: List[float] = []
    mem_maxs: List[float] = []
    mem_mins: List[float] = []
    total_rx = 0
    total_tx = 0

    for row in rows:
        bucket_ts, avg_cpu, max_cpu, min_cpu, avg_load, avg_mem, max_mem, min_mem, mem_total, sum_rx, sum_tx = row
        ts_ms = int(bucket_ts) * 1000
        rx_val = int(sum_rx or 0)
        tx_val = int(sum_tx or 0)
        total_rx += rx_val
        total_tx += tx_val

        cpu_avgs.append(float(avg_cpu or 0))
        cpu_maxs.append(float(max_cpu or 0))
        cpu_mins.append(float(min_cpu or 0))
        mem_avgs.append(float(avg_mem or 0))
        mem_maxs.append(float(max_mem or 0))
        mem_mins.append(float(min_mem or 0))

        points.append(
            {
                "time": ts_ms,
                "timestamp": ts_ms,
                "cpu": round((avg_cpu or 0.0) / 100.0, 4),
                "cpu_percent": round(float(avg_cpu or 0.0), 1),
                "loadavg": round(float(avg_load or 0.0), 2),
                "memtotal": int(mem_total or 0),
                "memused": int(avg_mem or 0),
                "memfree": max(0, int(mem_total or 0) - int(avg_mem or 0)),
                "netin": rx_val,
                "netout": tx_val,
            }
        )

    # Prefer real vnstat historical traffic when it captures active interfaces;
    # otherwise keep SQLite /proc/net/dev deltas (which always include Wi-Fi like wlp3s0).
    vnstat_data = _query_vnstat_network(timeframe, now, window_sec)
    if vnstat_data and vnstat_data["points"] and vnstat_data["total_rx"] >= total_rx:
        total_rx = vnstat_data["total_rx"]
        total_tx = vnstat_data["total_tx"]
        net_series = vnstat_data["points"]
    else:
        os_net = _read_proc_net_totals()
        if timeframe in ("day", "week", "month", "year"):
            oldest_ts = int(points[0]["time"] / 1000) if points else now
            if (now - oldest_ts) < (window_sec * 0.5):
                total_rx = max(total_rx, int(os_net.get("rx", 0)))
                total_tx = max(total_tx, int(os_net.get("tx", 0)))
        net_series = [{"time": p["time"], "rx": p["netin"], "tx": p["netout"]} for p in points]

    gb_div = 1024 ** 3
    mb_div = 1024 ** 2
    kb_div = 1024

    def _fmt_net(b: int) -> str:
        if b >= gb_div:
            return f"{round(b / gb_div, 2)} GB"
        if b >= mb_div:
            return f"{round(b / mb_div, 1)} MB"
        return f"{round(b / kb_div, 1)} KB"

    return {
        "data": points,
        "network_data": net_series,
        "timeframe": timeframe,
        "period_stats": {
            "cpu": {
                "avg": round(sum(cpu_avgs) / len(cpu_avgs), 1),
                "max": round(max(cpu_maxs), 1),
                "min": round(min(cpu_mins), 1),
            },
            "memory_used": {
                "avg": round((sum(mem_avgs) / len(mem_avgs)) / gb_div, 1),
                "max": round(max(mem_maxs) / gb_div, 1),
                "min": round(min(mem_mins) / gb_div, 1),
            },
            "network": {
                "rx_bytes": total_rx,
                "tx_bytes": total_tx,
                "rx_gb": round(total_rx / gb_div, 2),
                "tx_gb": round(total_tx / gb_div, 2),
                "rx_display": _fmt_net(total_rx),
                "tx_display": _fmt_net(total_tx),
            },
        },
        "last_checked": now * 1000,
        "cache_status": "real",
    }


def get_cached_updates(force_refresh: bool = False) -> Dict[str, Any]:
    """Return cached package updates and reboot status (5-min TTL)."""
    now = time.time()
    with _updates_cache_lock:
        if (
            not force_refresh
            and _updates_cache["updates"] is not None
            and (now - _updates_cache["timestamp"]) < _UPDATES_TTL_SECONDS
        ):
            return {
                "updates": _updates_cache["updates"],
                "reboot": _updates_cache["reboot"],
            }

    updates = check_updates(force_sync=force_refresh)
    reboot = check_reboot_required()
    with _updates_cache_lock:
        # Só grava no cache se não houve erro/timeout, ou se o cache ainda estiver vazio
        if not updates.get("error") or _updates_cache["updates"] is None:
            _updates_cache["timestamp"] = now
            _updates_cache["updates"] = updates
            _updates_cache["reboot"] = reboot
        else:
            updates = _updates_cache["updates"]
            reboot = _updates_cache["reboot"]

    return {"updates": updates, "reboot": reboot}


def invalidate_updates_cache() -> None:
    with _updates_cache_lock:
        _updates_cache["timestamp"] = 0.0
        _updates_cache["updates"] = None
        _updates_cache["reboot"] = None


def query_temperature_history(timeframe: str = "24h") -> Dict[str, Any]:
    """Query historical CPU temperature from SQLite for 1h/24h/7d/30d."""
    init_metrics_db()
    now = int(time.time())
    tf_map = {
        "1h": (3600, 60),
        "hour": (3600, 60),
        "24h": (86400, 600),
        "day": (86400, 600),
        "7d": (7 * 86400, 3600),
        "week": (7 * 86400, 3600),
        "30d": (30 * 86400, 14400),
        "month": (30 * 86400, 14400),
    }
    window_sec, bucket_sec = tf_map.get(timeframe, (86400, 600))
    since_ts = now - window_sec

    with _db_lock:
        conn = _get_conn()
        try:
            def _fetch_temp_buckets(b_sec: int):
                return conn.execute(
                    """
                    SELECT
                        (ts / ?) * ? AS bucket_ts,
                        AVG(temp_c) AS avg_temp,
                        MIN(temp_c) AS min_temp,
                        MAX(temp_c) AS max_temp
                    FROM system_samples
                    WHERE ts >= ? AND temp_c > 0
                    GROUP BY bucket_ts
                    ORDER BY bucket_ts ASC
                    """,
                    (b_sec, b_sec, since_ts),
                ).fetchall()

            rows = _fetch_temp_buckets(bucket_sec)
            if len(rows) < 6 and bucket_sec > 60:
                rows = _fetch_temp_buckets(60)
        finally:
            conn.close()

    live = get_real_temperature()
    live_temp = round(float(live.get("current", 0.0) or 0.0), 1)

    if not rows and live_temp > 0:
        record_sample()
        points = [{"time": now * 1000, "value": live_temp}]
        return {
            "data": points,
            "stats": {
                "current": live_temp,
                "min": live_temp,
                "avg": live_temp,
                "max": live_temp,
            },
            "timeframe": timeframe,
        }

    points = [
        {"time": int(b_ts) * 1000, "value": round(float(avg_t), 1)}
        for b_ts, avg_t, _, _ in rows
    ]
    mins = [float(r[2]) for r in rows]
    maxs = [float(r[3]) for r in rows]
    avgs = [float(r[1]) for r in rows]
    return {
        "data": points,
        "stats": {
            "current": live_temp if live_temp > 0 else (points[-1]["value"] if points else 0.0),
            "min": round(min(mins), 1) if mins else live_temp,
            "avg": round(sum(avgs) / len(avgs), 1) if avgs else live_temp,
            "max": round(max(maxs), 1) if maxs else live_temp,
        },
        "timeframe": timeframe,
    }
