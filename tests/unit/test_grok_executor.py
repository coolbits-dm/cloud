from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools import grok_executor


def test_execute_known_capability_contains_title():
    report = grok_executor.execute_capability("totp")
    assert "Time-based One-Time Password" in report
    assert "Operational checklist" in report


def test_execute_unknown_capability_raises_value_error():
    try:
        grok_executor.execute_capability("unknown")
    except ValueError as exc:
        assert "Unknown capability" in str(exc)
    else:  # pragma: no cover - clarity for future maintenance
        raise AssertionError("Expected ValueError for unknown capability")


def test_iter_capabilities_sorted():
    keys = [capability.key for capability in grok_executor.iter_capabilities()]
    assert keys == sorted(keys)
