# cblm/proto/iimsibis.py
from .envelope import new_envelope, sign, verify, Envelope as IimsibisEnvelope
VER = "iimsibis-0.1"; KEY_ENV = "IIMSIBIS_HMAC_KEY"
def make_event(src, dst, body): return new_envelope(VER, "event", src, dst, body)
def sign_env(env): return sign(env, KEY_ENV)
def verify_env(env, replay_db=None): return verify(env, KEY_ENV, replay_db=replay_db)
