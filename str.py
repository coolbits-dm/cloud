# Secure str.py redirector - PIN required
# This file redirects to the secure version in app/andrei/secure/str.py

from __future__ import annotations
import sys
import os

# Redirect to secure version
secure_path = os.path.join(os.path.dirname(__file__), "app", "andrei", "secure", "str.py")
if os.path.exists(secure_path):
    with open(secure_path, 'r', encoding='utf-8') as f:
        exec(f.read())
else:
    print("Secure str.py not found. Please check file path.")

# --- M16 UTF-8 Safe Utilities (Additive) ---
import json, io, os, re, tempfile, hashlib, unicodedata
from contextlib import contextmanager
from typing import Any, Iterable, Optional

__all__ = [
    # EOL & encoding
    "s_to_utf8", "s_normalize_eol", "s_read_text", "s_write_text_atomic",
    # JSON
    "s_json_load", "s_json_dump_atomic", "s_json_merge",
    # Strings
    "s_slug", "s_trim_multi", "s_collapse_ws",
    # Hash
    "s_sha256_hex", "s_file_sha256_hex",
    # M17 Environment & Path helpers
    "s_env_get", "s_path_norm",
    # M18 Extensions
    "atomic_json_patch", "stable_uuid", "ts_now_iso", "cbt_posting_cost",
    "rag_path", "guard_noninteractive", "env_mode"
]

# --- EOL & encoding ---------------------------------------------------------

def s_to_utf8(s: Any) -> str:
    if s is None:
        return ""
    if isinstance(s, bytes):
        return s.decode("utf-8", errors="replace")
    return str(s)

def s_normalize_eol(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # fără trailing newline în exces
    return re.sub(r"\n+\Z", "\n", s)

def s_read_text(path: str, fallback_encoding: str = "utf-8") -> str:
    with io.open(path, "r", encoding=fallback_encoding, errors="strict") as f:
        data = f.read()
    return s_normalize_eol(data)

def s_write_text_atomic(path: str, data: str, encoding: str = "utf-8") -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = s_normalize_eol(s_to_utf8(data))
    dir_name = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=dir_name)
    try:
        with io.open(fd, "w", encoding=encoding, errors="strict") as f:
            f.write(data)
        os.replace(tmp_path, path)  # atomic pe același FS
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass

# --- JSON safe --------------------------------------------------------------

def s_json_load(path: str) -> Any:
    text = s_read_text(path)
    return json.loads(text)

def s_json_dump_atomic(path: str, obj: Any, ensure_ascii: bool = False) -> None:
    # sort_keys pentru determinism, indent 2 ca să nu-ți umflu diff-ul
    text = json.dumps(obj, ensure_ascii=ensure_ascii, sort_keys=True, indent=2)
    s_write_text_atomic(path, text + "\n")

# --- Strings helpers --------------------------------------------------------

def s_slug(s: str, max_len: int = 80) -> str:
    s = s_to_utf8(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:max_len] or "n-a"

def s_trim_multi(*parts: Optional[str]) -> str:
    return " ".join(p.strip() for p in parts if p and p.strip())

def s_collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

# --- Hashing ----------------------------------------------------------------

def s_sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def s_file_sha256_hex(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# --- M17 Environment & Path helpers -------------------------------------------

def s_env_get(key: str, default: str = "") -> str:
    """Citire sigură din environment variables cu fallback."""
    return os.environ.get(key, default)

def s_path_norm(path: str) -> str:
    """Normalizează căi cross-platform (Windows/Unix)."""
    return os.path.normpath(os.path.normcase(path))

def s_json_merge(base: dict, overlay: dict) -> dict:
    """Combină JSON-uri recursiv (pentru panel updates)."""
    result = base.copy()
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = s_json_merge(result[key], value)
        else:
            result[key] = value
    return result

# --- M18 Extensions -----------------------------------------------------------

import datetime
import jsonschema
from pathlib import Path

def atomic_json_patch(path: str, payload: dict, schema: Optional[str] = None) -> None:
    """Validează cu schema dacă există, apoi scrie atomic (tmp + rename)."""
    if schema and os.path.exists(schema):
        with open(schema, 'r', encoding='utf-8') as f:
            schema_obj = json.load(f)
        jsonschema.validate(payload, schema_obj)
    
    s_json_dump_atomic(path, payload)

def stable_uuid(*parts: str) -> str:
    """Pentru ID-uri determinate din content."""
    content = "|".join(str(p) for p in parts)
    return s_sha256_hex(content)[:16]

def ts_now_iso() -> str:
    """Returnează ISO8601 cu tz."""
    return datetime.datetime.utcnow().isoformat() + "Z"

def cbt_posting_cost(kind: str) -> float:
    """Map la tarifar."""
    tariff = {
        "WALL_POST": -1.0,
        "NHA_INVOCATION": -2.0,
        "BOARD_MEETING": -3.0,
        "BITS_DRY_RUN": -1.0
    }
    return tariff.get(kind, 0.0)

def rag_path(panel: str) -> Path:
    """Centralizează rutele RAG."""
    return Path(f"cblm/rag/store/{panel}.json")

def guard_noninteractive() -> None:
    """Early exit dacă TTY/STDIN interactiv."""
    if sys.stdin.isatty():
        print("ERROR: Interactive mode detected. M18 requires non-interactive execution.")
        sys.exit(1)

def env_mode() -> str:
    """Returnează dev|prod, dar 100% dev implicit."""
    mode = s_env_get("CB_BILLING_MODE", "dev")
    if mode not in ["dev", "prod"]:
        return "dev"
    return mode