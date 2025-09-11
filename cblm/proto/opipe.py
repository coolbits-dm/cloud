# cblm/proto/opipe.py
from .envelope import new_envelope, sign, verify, Envelope as PipeEnvelope

VER = "opipe-0.1"
KEY_ENV = "OPIPE_HMAC_KEY"

def make_event(src: str, dst: list[str], body: dict) -> PipeEnvelope:
    return new_envelope(VER, "event", src, dst, body)

def sign_env(env: PipeEnvelope) -> PipeEnvelope:
    return sign(env, KEY_ENV)

def verify_env(env: PipeEnvelope, replay_db=None) -> None:
    return verify(env, KEY_ENV, replay_db=replay_db)
