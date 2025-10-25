"""Executor wrapper for Claude daemon."""

from __future__ import annotations

from typing import Any, Dict, List


def _summarise_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    title = spec.get("title") if isinstance(spec.get("title"), str) else "Unnamed design"
    goal = spec.get("goal") if isinstance(spec.get("goal"), str) else None
    acceptance = spec.get("acceptance") if isinstance(spec.get("acceptance"), list) else []
    changes = spec.get("changes") if isinstance(spec.get("changes"), list) else []

    acceptance_lines: List[str] = []
    for entry in acceptance:
        if isinstance(entry, str):
            acceptance_lines.append(entry)
        else:
            acceptance_lines.append(str(entry))

    change_lines: List[str] = []
    for entry in changes:
        if isinstance(entry, dict):
            path = entry.get("path") or entry.get("file")
            action = entry.get("action")
            detail = entry.get("description") or entry.get("detail")
            change_lines.append(" • ".join(filter(None, [action, path, detail])))
        else:
            change_lines.append(str(entry))

    return {
        "title": title,
        "goal": goal,
        "acceptance": acceptance_lines,
        "changes": change_lines,
    }


def execute(task: str, parameters: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Placeholder executor; to be implemented with Claude MCP bindings."""
    parameters = parameters or {}

    if task == "apply_spec":
        spec = parameters.get("spec") if isinstance(parameters.get("spec"), dict) else {}
        prompt = parameters.get("prompt") if isinstance(parameters.get("prompt"), str) else None
        summary = _summarise_spec(spec)
        output_lines = [
            f"Claude Code received the design \"{summary['title']}\".",
        ]
        if summary["goal"]:
            output_lines.append(f"Primary goal: {summary['goal']}")

        if summary["acceptance"]:
            output_lines.append("Acceptance criteria:")
            output_lines.extend(f"- {line}" for line in summary["acceptance"])

        if summary["changes"]:
            output_lines.append("Planned changes:")
            output_lines.extend(f"- {line}" for line in summary["changes"])

        if prompt:
            output_lines.append(f"Archon summary: {prompt}")

        output_lines.append("Status: ready for Claude Code application (stub).")

        return {
            "task": task,
            "parameters": parameters,
            "output": "\n".join(output_lines),
            "success": True,
            "summary": summary,
        }

    return {
        "task": task,
        "parameters": parameters,
        "output": "Claude execution stub",
        "success": True,
    }
