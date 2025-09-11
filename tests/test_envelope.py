# tests/test_envelope.py
import os, time
from cblm.proto.envelope import new_envelope, sign, verify

def test_hmac_and_ttl_ok(monkeypatch):
    monkeypatch.setenv("OPIPE_HMAC_KEY", "secret")
    env = new_envelope("opipe-0.1","event","ogpt01/CEO",["ocursor"],{"x":1},ttl_s=5)
    sign(env,"OPIPE_HMAC_KEY")
    verify(env,"OPIPE_HMAC_KEY", replay_db=set())

def test_replay_detected(monkeypatch):
    monkeypatch.setenv("OPIPE_HMAC_KEY", "secret")
    env = new_envelope("opipe-0.1","event","ogpt01/CEO",["ocursor"],{"x":1},ttl_s=5)
    sign(env,"OPIPE_HMAC_KEY")
    db=set()
    verify(env,"OPIPE_HMAC_KEY", replay_db=db)
    try:
        verify(env,"OPIPE_HMAC_KEY", replay_db=db)
        assert False, "expected replay"
    except ValueError:
        assert True

def test_expired(monkeypatch):
    monkeypatch.setenv("OPIPE_HMAC_KEY", "secret")
    env = new_envelope("opipe-0.1","event","ogpt01/CEO",["ocursor"],{"x":1},ttl_s=1)
    sign(env,"OPIPE_HMAC_KEY")
    time.sleep(1.1)  # sleep longer than TTL
    try:
        verify(env,"OPIPE_HMAC_KEY", replay_db=set())
        assert False, "expected expired"
    except ValueError:
        assert True
