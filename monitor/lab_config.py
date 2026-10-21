"""
SmartFix AI — Lab Monitor Shared Config & Protocol
Handles seat name persistence, protocol message helpers, and shared constants.
"""
import json
import os
import socket
from typing import Any, Dict, Optional

LAB_PORT = 7771
LAB_AGENT_VERSION = "1.0"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "lab_config.json")

# ── Message types ──────────────────────────────────────────────────────────────
MSG_PING          = "PING"
MSG_PONG          = "PONG"
MSG_STATUS        = "STATUS"          # Agent -> Admin: full status snapshot
MSG_REPAIR        = "REPAIR"          # Admin -> Agent: trigger a repair
MSG_REPAIR_RESULT = "REPAIR_RESULT"   # Agent -> Admin: result of a repair
MSG_GET_STATUS    = "GET_STATUS"      # Admin -> Agent: request a fresh status
MSG_SET_SEAT      = "SET_SEAT"        # Internal use
MSG_SHUTDOWN      = "SHUTDOWN"        # Admin -> Agent: graceful stop (future)


def _ensure_data_dir():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)


def load_lab_config() -> Dict[str, Any]:
    """Load lab config from disk. Returns defaults if not found."""
    _ensure_data_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"seat_name": "", "mode": "unset"}  # mode: "admin" | "client" | "unset"


def save_lab_config(cfg: Dict[str, Any]):
    """Persist lab config to disk."""
    _ensure_data_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def get_seat_name() -> str:
    return load_lab_config().get("seat_name", "")


def set_seat_name(name: str):
    cfg = load_lab_config()
    cfg["seat_name"] = name
    save_lab_config(cfg)


def get_mode() -> str:
    return load_lab_config().get("mode", "unset")


def set_mode(mode: str):
    cfg = load_lab_config()
    cfg["mode"] = mode
    save_lab_config(cfg)


def get_local_ip() -> str:
    """Get this machine's LAN IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_known_clients() -> list:
    """Return list of known client entries: [{seat, ip, port}]."""
    return load_lab_config().get("known_clients", [])


def save_known_clients(clients: list):
    cfg = load_lab_config()
    cfg["known_clients"] = clients
    save_lab_config(cfg)


def make_message(msg_type: str, payload: Optional[Dict] = None) -> bytes:
    """Encode a message as newline-terminated JSON."""
    msg = {"type": msg_type, "payload": payload or {}}
    return (json.dumps(msg) + "\n").encode("utf-8")


def parse_message(raw: str) -> Optional[Dict[str, Any]]:
    """Decode a JSON message string. Returns None on parse error."""
    try:
        return json.loads(raw.strip())
    except Exception:
        return None


def send_message(sock: socket.socket, msg_type: str, payload: Optional[Dict] = None) -> bool:
    """Send a framed JSON message over a socket. Returns True on success."""
    try:
        sock.sendall(make_message(msg_type, payload))
        return True
    except Exception:
        return False


def recv_message(sock: socket.socket, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """Receive one newline-terminated JSON message from a socket."""
    sock.settimeout(timeout)
    buf = b""
    try:
        while b"\n" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                return None
            buf += chunk
        line = buf.split(b"\n", 1)[0]
        return parse_message(line.decode("utf-8"))
    except Exception:
        return None
