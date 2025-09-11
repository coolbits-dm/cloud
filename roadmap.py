# roadmap.py — canon pentru CoolBits.ai | cbLM.ai
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Literal

DATA_PATH = os.environ.get("ROADMAP_JSON", os.path.join("data", "roadmap.json"))
Status = Literal["todo", "doing", "done", "blocked"]


@dataclass
class Task:
    id: str
    title: str
    owner: str
    status: Status = "todo"
    notes: str = ""


@dataclass
class Milestone:
    id: str
    title: str
    tasks: List[Task]


@dataclass
class Roadmap:
    version: str
    milestones: List[Milestone]


DEFAULT = Roadmap(
    version="2025-09-10",
    milestones=[
        Milestone(
            "M1",
            "Stabilitate beton",
            tasks=[
                Task("M1-T1", "Server HTTP robust + retry", "oRunner", "done"),
                Task("M1-T2", "Rate limiting + timeouts + audit", "oRunner", "done"),
                Task("M1-T3", "Smoke tests + baseline perf", "oRunner", "done"),
            ],
        ),
        Milestone(
            "M2",
            "Mock→Real integrare execuții",
            tasks=[
                Task("M2-T1", "GPU real (nvidia-smi)", "oRunner", "done"),
                Task("M2-T2", "Cursor real (launch proiect)", "oRunner", "done"),
                Task("M2-T3", "GCloud real (auth, run describe)", "oRunner", "done"),
                Task("M2-T4", "RAG real (bridge 8765)", "oRunner", "done"),
            ],
        ),
        Milestone(
            "M3",
            "Paritate cloud & CI gates",
            tasks=[
                Task("M3-T1", "Health cu commitSha/buildTime/node", "oPyGPT03", "done"),
                Task(
                    "M3-T2", "CI: lint/typecheck/test/e2e + docker", "oPyGPT03", "done"
                ),
                Task("M3-T3", "Staging canary + rollback script", "oPyGPT03", "done"),
            ],
        ),
        Milestone(
            "M4",
            "Hardening & UX",
            tasks=[
                Task("M4-T1", "RBAC + HMAC pentru POST sensibile", "oPyGPT03", "done"),
                Task("M4-T2", "Uptime checks + alerte p95/5xx", "oPyGPT03", "done"),
                Task(
                    "M4-T3",
                    "UI: status live, port din .runtime.json",
                    "oRunner",
                    "todo",
                ),
            ],
        ),
        Milestone(
            "M5",
            "Validare Practică",
            tasks=[
                Task("M5-T1", "Test CI pipeline cu commit dummy", "oPyGPT03", "done"),
                Task("M5-T2", "Test canary deployment cu bug", "oPyGPT03", "done"),
                Task("M5-T3", "Test RBAC/HMAC cu user wrong role", "oPyGPT03", "done"),
                Task(
                    "M5-T4",
                    "Test uptime monitor cu RAG/GPU offline",
                    "oPyGPT03",
                    "todo",
                ),
                Task("M5-T5", "Integrare HMAC key real în manager", "oPyGPT03", "done"),
                Task(
                    "M5-T6", "Dashboard conectat la API-uri reale", "oPyGPT03", "done"
                ),
            ],
        ),
    ],
)


def load() -> Roadmap:
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        save(DEFAULT)
        return DEFAULT
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    ms = []
    for m in data["milestones"]:
        ms.append(
            Milestone(
                id=m["id"], title=m["title"], tasks=[Task(**t) for t in m["tasks"]]
            )
        )
    return Roadmap(version=data["version"], milestones=ms)


def save(r: Roadmap) -> None:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(r), f, ensure_ascii=False, indent=2)


def set_status(task_id: str, status: Status, note: str = "") -> None:
    r = load()
    for m in r.milestones:
        for t in m.tasks:
            if t.id == task_id:
                t.status = status
                if note:
                    t.notes = note
                save(r)
                return
    raise SystemExit(f"Task not found: {task_id}")


def list_all() -> None:
    r = load()
    for m in r.milestones:
        print(f"[{m.id}] {m.title}")
        for t in m.tasks:
            print(
                f"  - {t.id:6} [{t.status:6}] {t.title}  @{t.owner}  {('* ' + t.notes) if t.notes else ''}"
            )


if __name__ == "__main__":
    # CLI: python roadmap.py list | set M2-T1 done "implemented real GPU"
    if len(sys.argv) < 2:
        print(
            "usage: python roadmap.py list | set <TASK_ID> <todo|doing|done|blocked> [note]"
        )
        sys.exit(1)
    if sys.argv[1] == "list":
        list_all()
        sys.exit(0)
    if sys.argv[1] == "set":
        _, _, tid, st, *note = sys.argv
        set_status(tid, st, " ".join(note))
        sys.exit(0)
    print("unknown command")
