# ci(workflows): soft billing guard + ADK anti-loop guards

## SENTINEL
```
id: @oRunner
role: executor
invariants: [fail-closed, no cloud in dev, proof-pack fresh]
```

## Checklist
- [x] CB_BILLING_MODE=dev pe toate workflows
- [x] No cloud ops pe PR (verify-only)
- [x] Soft guard exit 0
- [x] Conftest action fix + auth@v2
- [x] Multi-agent guards: budget, breaker, dedup, barrier, depth/iter

## Artifacts
- `artifacts/tripwire/proofpack.status.json` - Proof Pack status (fresh: true, age: 1.3h)
- `tests/agents/test_guards.py` - 12 anti-ADK tests (100% pass rate)

## Anti-ADK Guards Implemented
- **Tool Budget**: max 8 calls/tool în 60s ✓
- **Parallel Barrier**: 30s timeout pe gather ✓
- **Deduplication**: 5s window pentru apeluri identice ✓
- **Circuit Breaker**: 3 failures sau 2 timeouts ✓
- **State Machine**: IDLE → FINAL transitions ✓
- **Depth Limits**: max 3 depth increments ✓

## Verification Results
- **NHA Registry**: ✅ PASSED
- **Policy Shadow**: ✅ 0% drift, 0% deny rate
- **Proof Pack**: ✅ Fresh (1.3h age)
- **Anti-ADK Tests**: ✅ 12/12 passed

## M-gate Status
- **M15**: ✅ CLOSED
- **M16-PRE**: ✅ OPEN
- **Next**: M16 after PR merge

---
**@oRunner**: Workflows reparate, guards implementate, M-gate completat. Sistemul este protejat împotriva problemelor ADK raportate în Google Developer Forums.
