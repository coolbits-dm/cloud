# cblm/proto/oilluminate.py
from .envelope import new_envelope, sign, verify, Envelope as IlluminateEnvelope
VER = "oilluminate-0.1"; KEY_ENV = "OILLUMINATE_HMAC_KEY"
def make_event(src, dst, body): return new_envelope(VER, "event", src, dst, body)
def sign_env(env): return sign(env, KEY_ENV)
def verify_env(env, replay_db=None): return verify(env, KEY_ENV, replay_db=replay_db)
