"""Hardened Archon orchestrator for ArcaneOS."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.config import settings
from app.services.daemon_registry import daemon_registry
from app.services.raindrop_client import MCPToolResult, ModelProvider, get_mcp_client
from app.services.spell_parser import ParseError, SpellAction, get_spell_parser

from ArcaneOS.core.audio_bus import get_audio_bus
from ArcaneOS.core.event_bus import get_event_bus
from ArcaneOS.core.safety import validate_archon_payload
from ArcaneOS.core.schemas import DaemonType
from ArcaneOS.core.veil import is_fantasy_mode

logger = logging.getLogger(__name__)

SIMPLE_LATENCY_BUDGET = 0.6
CODEGEN_LATENCY_BUDGET = 2.5


@dataclass
class ArchonDecision:
    intent: str
    target_daemon: Optional[DaemonType]
    task: Optional[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    plan: List[str] = field(default_factory=list)
    narration: str = field(default_factory=lambda: settings.archon_base_narration)
    reasoning: str = ""
    confidence: Optional[float] = None
    fallback_used: bool = False
    raw: Dict[str, Any] = field(default_factory=dict)
    parsed_summary: Dict[str, Any] = field(default_factory=dict)


class ArchonRouter:
    def __init__(self) -> None:
        self._parser = get_spell_parser()
        self._client = get_mcp_client()
        self._audio = get_audio_bus()
        self._event_bus = get_event_bus()
        self._tool_registered = False
        if settings.archon_enabled:
            self._register_archon_tool()

    def _register_archon_tool(self) -> None:
        if self._tool_registered:
            return
        try:
            success = self._client.register_tool(
                tool_name=settings.archon_tool_name,
                model=settings.archon_model_id,
                provider=ModelProvider.CUSTOM,
                capabilities=["routing", "planning", "analysis"],
                metadata={"role": settings.archon_role_name},
            )
            self._tool_registered = success
            if success:
                logger.info("Archon tool registered with model %s", settings.archon_model_id)
        except Exception as exc:
            logger.error("Archon registration error: %s", exc)
            self._tool_registered = False

    def analyze_spell(self, spell_text: str) -> ArchonDecision:
        return self._generate_decision(spell_text)

    def route_spell(self, spell_text: str) -> Dict[str, Any]:
        decision = self._generate_decision(spell_text)
        execution = self.execute_decision(decision)

        fantasy_mode = is_fantasy_mode()
        archon_payload = {
            "role": settings.archon_role_name,
            "narration": decision.narration if fantasy_mode else decision.reasoning,
            "reasoning": decision.reasoning,
            "fallback_used": decision.fallback_used,
            "chain_of_thought": decision.raw.get("plan", decision.plan),
            "confidence": decision.confidence,
            "raw_decision": decision.raw,
        }
        if not fantasy_mode:
            archon_payload["dev_mode"] = True

        return {
            "success": True,
            "archon": archon_payload,
            "parsed": decision.parsed_summary,
            "execution": execution,
        }

    def execute_decision(self, decision: ArchonDecision) -> Dict[str, Any]:
        return self._execute_decision(decision)

    # Internal -----------------------------------------------------------------

    def _generate_decision(self, spell_text: str) -> ArchonDecision:
        fantasy_mode = is_fantasy_mode()
        if settings.archon_enabled and self._tool_registered:
            try:
                payload, latency = self._request_archon_directive(spell_text)
                cleaned = validate_archon_payload(payload, fantasy_mode)
                decision = self._decision_from_payload(spell_text, cleaned)
                self._apply_latency_policy(decision, latency)
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop:
                    loop.create_task(
                        self._event_bus.emit_route(
                            daemon_name=decision.target_daemon.value if decision.target_daemon else "none",
                            success=True,
                            metadata={
                                "latency_ms": round(latency * 1000, 2),
                                "intent": decision.intent,
                                "fantasy": fantasy_mode,
                            },
                        )
                    )
                else:
                    logger.debug("No running event loop; skipping async route emit.")
                self._audio.speak("archon", "route")
                return decision
            except (ValueError, HTTPException) as exc:
                logger.warning("Archon directive rejected: %s", exc)
            except Exception as exc:
                logger.error("Archon directive error: %s", exc)

        return self._decision_from_spell_parser(spell_text)

    def _request_archon_directive(self, spell_text: str) -> tuple[Dict[str, Any], float]:
        system_prompt = settings.archon_system_prompt
        attempts = [system_prompt, system_prompt + "\nReturn only JSON. No prose."]
        last_error: Optional[Exception] = None
        for prompt in attempts:
            started = time.perf_counter()
            task = (
                f"{prompt}\n\nUser Spell: \"{spell_text}\"\n"
                "Remember: respond with strict JSON only."
            )
            result: MCPToolResult = self._client.invoke_tool(
                tool_name=settings.archon_tool_name,
                task=task,
                parameters={"mode": "orchestration", "model": settings.archon_model_id},
            )
            latency = time.perf_counter() - started
            raw_output = result.result.get("output") if isinstance(result.result, dict) else None
            if not raw_output:
                last_error = ValueError("empty_output")
                continue
            try:
                payload = json.loads(raw_output)
                if isinstance(payload, dict):
                    payload.setdefault("plan", payload.get("plan", []))
                    return payload, latency
            except json.JSONDecodeError as exc:
                last_error = exc
        raise ValueError(f"invalid_archon_output: {last_error}")

    def _decision_from_payload(self, spell_text: str, payload: Dict[str, Any]) -> ArchonDecision:
        intent = payload.get("intent", "").lower()
        daemon_value = payload.get("daemon", "none")
        target_daemon = None
        try:
            target_daemon = DaemonType(daemon_value)
        except ValueError:
            target_daemon = None

        task = payload.get("task")
        plan = payload.get("plan", [])
        parsed_summary = {
            "action": intent,
            "daemon": target_daemon.value if target_daemon else None,
            "task": task,
            "parameters": payload.get("parameters"),
            "raw_input": spell_text,
        }

        narration = settings.archon_base_narration if payload.get("style", {}).get("fantasy", True) else payload.get(
            "reasoning", ""
        )
        reasoning = payload.get("reasoning", "")
        confidence = payload.get("confidence")

        return ArchonDecision(
            intent=intent,
            target_daemon=target_daemon,
            task=task,
            parameters=payload.get("parameters", {}),
            plan=plan,
            narration=narration,
            reasoning=reasoning,
            confidence=confidence,
            raw=payload,
            parsed_summary=parsed_summary,
        )

    def _decision_from_spell_parser(self, spell_text: str) -> ArchonDecision:
        try:
            parsed = self._parser.parse(spell_text)
            intent = parsed.action.value if isinstance(parsed.action, SpellAction) else str(parsed.action)
            target = None
            if parsed.daemon:
                try:
                    target = DaemonType(parsed.daemon)
                except ValueError:
                    target = None
            plan = parsed.parameters.get("plan", []) if parsed.parameters else []
            return ArchonDecision(
                intent=intent,
                target_daemon=target,
                task=parsed.task,
                parameters=parsed.parameters or {},
                plan=plan if isinstance(plan, list) else [],
                narration=(
                    f"{settings.archon_role_name} contemplates your words, relying on ancient heuristics." if is_fantasy_mode() else "parser_fallback"
                ),
                reasoning="Fallback spell parser engaged.",
                confidence=0.6,
                fallback_used=True,
                raw=parsed.to_dict(),
                parsed_summary={**parsed.to_dict(), "raw_input": spell_text},
            )
        except ParseError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def _apply_latency_policy(self, decision: ArchonDecision, latency: float) -> None:
        is_codegen = decision.intent == "invoke" and decision.target_daemon == DaemonType.CLAUDE
        simple_spell = not is_codegen

        if simple_spell and latency > SIMPLE_LATENCY_BUDGET:
            decision.fallback_used = True
            decision.plan.insert(0, "Latency exceeded simple budget; rerouting to LiquidMetal.")
            decision.raw["daemon"] = "liquidmetal"
            decision.target_daemon = DaemonType.LIQUIDMETAL
        elif is_codegen and latency > CODEGEN_LATENCY_BUDGET:
            decision.fallback_used = True
            decision.plan.insert(0, "Codegen latency too high; delegating to LiquidMetal summary.")
            decision.raw["daemon"] = "liquidmetal"
            decision.target_daemon = DaemonType.LIQUIDMETAL

    def _execute_decision(self, decision: ArchonDecision) -> Dict[str, Any]:
        daemon = decision.target_daemon
        if daemon is None:
            plan = decision.plan or ["No safe execution path provided."]
            raise HTTPException(status_code=422, detail={"plan": plan})

        if daemon == DaemonType.CLAUDE:
            result = daemon_registry.invoke_daemon(daemon, decision.task or "", decision.parameters)
        elif daemon == DaemonType.GEMINI:
            result = daemon_registry.invoke_daemon(daemon, decision.task or "", decision.parameters)
        elif daemon == DaemonType.LIQUIDMETAL:
            result = daemon_registry.invoke_daemon(daemon, decision.task or "", decision.parameters)
        else:
            raise HTTPException(status_code=422, detail={"plan": decision.plan or []})

        return result


_archon_router: Optional[ArchonRouter] = None


def get_archon_router() -> ArchonRouter:
    global _archon_router
    if _archon_router is None:
        _archon_router = ArchonRouter()
    return _archon_router
