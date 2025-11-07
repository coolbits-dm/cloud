"""Command line interface for querying oGrok execution capabilities."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from tools.grok_executor import execute_capability, iter_capabilities


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grok",
        description="Interact with the oGrok execution catalogue.",
    )
    parser.add_argument(
        "--format",
        choices={"text", "json"},
        default="text",
        help="Output format for responses (default: text).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    execute_parser = subparsers.add_parser(
        "execute", help="Render the execution checklist for a capability."
    )
    execute_parser.add_argument("capability", help="Capability key to execute.")

    subparsers.add_parser("list", help="List available capability keys.")

    return parser


def render_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def handle_execute(capability: str, output_format: str) -> str:
    if output_format == "json":
        capability_obj = execute_capability(capability)
        return render_json({"capability": capability, "report": capability_obj})
    return execute_capability(capability)


def handle_list(output_format: str) -> str:
    if output_format == "json":
        data = {
            "capabilities": [capability.key for capability in iter_capabilities()],
        }
        return render_json(data)

    capability_lines = [
        f"- {capability.key}: {capability.title}" for capability in iter_capabilities()
    ]
    return "Available Grok capabilities:\n" + "\n".join(capability_lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "execute":
            output = handle_execute(args.capability, args.format)
        elif args.command == "list":
            output = handle_list(args.format)
        else:  # pragma: no cover - argparse prevents this branch
            parser.error(f"Unknown command: {args.command}")
            return 2
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

