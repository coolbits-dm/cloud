# cblm/proto/envelope.py
from __future__ import annotations
import hmac, hashlib, os, time, json, secrets
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

@dataclass
class Envelope:
    ver: str           # ex: opipe-0.1 | oilluminate-0.1 | iimsibis-0.1
    typ: str           # heartbeat | event | command | ack
    id: str            # uuid/ksuid
    ts: float          # epoch seconds
    src: str           # agent/role, ex: ogpt01/CEO
    dst: list[str]     # destinatari
    agent_type: str    # human | non-human (pentru @oNHA)
    corr: Optional[str] = None
    ttl_s: int = 300
    nonce: str = ""
    sig: Optional[str] = None
    body: Dict[str, Any] = None  # payload

    def to_dict(self, include_sig: bool = True) -> Dict[str, Any]:
        d = asdict(self)
        if not include_sig:
            d.pop("sig", None)
        return d

def _secret(key_env: str) -> bytes:
    k = os.getenv(key_env)
    if not k:
        raise RuntimeError(f"Missing secret in env: {key_env}")
    return k.encode("utf-8")

def sign(env: Envelope, key_env: str) -> Envelope:
    data = json.dumps(env.to_dict(include_sig=False), separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(_secret(key_env), data, hashlib.sha256).hexdigest()
    env.sig = sig
    return env

def verify(env: Envelope, key_env: str, replay_db: Optional[set[str]] = None) -> None:
    # ttl
    now = time.time()
    if env.ttl_s and now - env.ts > env.ttl_s:
        raise ValueError("Envelope expired")
    # replay
    if replay_db is not None:
        if env.nonce in replay_db:
            raise ValueError("Replay detected")
        replay_db.add(env.nonce)
    # hmac
    expected = sign(Envelope(**{**env.to_dict(), "sig": None}), key_env).sig
    if not hmac.compare_digest(env.sig or "", expected or ""):
        raise ValueError("Bad HMAC signature")

def new_envelope(ver: str, typ: str, src: str, dst: list[str], body: Dict[str, Any], agent_type: str = "human", ttl_s: int = 300) -> Envelope:
    return Envelope(
        ver=ver, typ=typ, id=_ksuid(), ts=time.time(), src=src, dst=dst,
        agent_type=agent_type, corr=None, ttl_s=ttl_s, nonce=_nonce(), sig=None, body=body
    )

def _nonce() -> str:
    return secrets.token_urlsafe(16)

def _ksuid() -> str:
    return secrets.token_urlsafe(20)
