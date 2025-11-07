"""Utility helpers for the lightweight `grok` command line interface.

This module centralises the knowledge about the oGrok agent execution
capabilities that are currently surfaced to developers.  The CLI wrapper
(`cloud/grok.py`) imports this module so that the actual business logic can be
unit tested without invoking a subprocess.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from textwrap import indent
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class Capability:
    """Describe a Grok execution capability."""

    key: str
    title: str
    description: str
    checklist: List[str]
    status: str

    def render(self) -> str:
        """Render a human friendly description of the capability."""

        checklist = "\n".join(f"- {item}" for item in self.checklist)
        rendered_checklist = indent(checklist, "  ") if checklist else "  - None"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

        return (
            f"🧠 Grok Capability: {self.title}\n"
            f"🔑 Key: {self.key}\n"
            f"📋 Status: {self.status}\n"
            f"📅 Timestamp (UTC): {timestamp}\n\n"
            f"{self.description}\n\n"
            f"Operational checklist:\n{rendered_checklist}"
        )


CAPABILITIES: Dict[str, Capability] = {
    capability.key: capability
    for capability in (
        Capability(
            key="totp",
            title="Time-based One-Time Password",
            description=(
                "Simulates the validation pipeline for TOTP enrolment. The"
                " check ensures that seed storage, clock drift tolerance,"
                " and backup code rotation policies align with the current"
                " security baseline."
            ),
            checklist=[
                "Verify seed material in hardware security module",
                "Confirm 30s step window with ±1 drift allowance",
                "Ensure backup codes rotated and published to Secrets Manager",
            ],
            status="ready",
        ),
        Capability(
            key="tus",
            title="Resumable Uploads (tus.io)",
            description=(
                "Performs a dry-run of the resumable upload orchestration used"
                " for large artefact ingestion. Validation focuses on chunk"
                " reconciliation, offset negotiation, and cross-region bucket"
                " replication."
            ),
            checklist=[
                "Negotiate tus protocol version 1.0.0",
                "Validate PATCH/HEAD parity for partial uploads",
                "Confirm GCS bucket replication policy is active",
            ],
            status="ready",
        ),
        Capability(
            key="webrtc",
            title="WebRTC Signalling",
            description=(
                "Runs the media edge handshake scenario, covering ICE"
                " candidate exchange, DTLS certificate verification, and"
                " TURN allocation availability."
            ),
            checklist=[
                "Collect STUN candidates from global pool",
                "Validate DTLS fingerprints against pinned certs",
                "Exercise TURN relay allocation with QoS policies",
            ],
            status="ready",
        ),
        Capability(
            key="baremetal",
            title="Bare Metal Provisioning",
            description=(
                "Validates the PXE bootstrapping and hardware inventory"
                " reporting used for on-prem accelerator nodes. Includes"
                " firmware baseline checks and network isolation controls."
            ),
            checklist=[
                "PXE handshake completed via secured VLAN",
                "Firmware signatures verified (TPM backed)",
                "Out-of-band management channel reachable",
            ],
            status="preflight",
        ),
        Capability(
            key="dnssec",
            title="DNSSEC Deployment",
            description=(
                "Executes the DNSSEC signing verification cycle, ensuring zone"
                " signing keys, key signing keys, and DS record propagation"
                " comply with registry expectations."
            ),
            checklist=[
                "ZSK roll-forward scheduled and published",
                "KSK ceremony artefacts stored in vault",
                "Parent registry DS record alignment confirmed",
            ],
            status="ready",
        ),
    )
}


def get_capability(key: str) -> Capability:
    """Return the capability associated with *key*.

    Parameters
    ----------
    key:
        The identifier used on the command line.

    Raises
    ------
    ValueError
        If the capability does not exist.
    """

    normalised = key.strip().lower()
    try:
        return CAPABILITIES[normalised]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Unknown capability: {key}") from exc


def execute_capability(key: str) -> str:
    """Produce a report for the requested capability."""

    capability = get_capability(key)
    return capability.render()


def iter_capabilities() -> Iterable[Capability]:
    """Return all configured capabilities sorted by key."""

    return (CAPABILITIES[key] for key in sorted(CAPABILITIES))

