from typing import Any, Dict

import pytest
from fastapi import HTTPException

from ArcaneOS.core.archon_router import ArchonRouter
from ArcaneOS.core import grimoire
from ArcaneOS.core.safety import validate_archon_payload
from ArcaneOS.core.schemas import DaemonType
from ArcaneOS.core.veil import set_veil
from app.services.daemon_registry import daemon_registry


@pytest.mark.parametrize("fantasy_mode", [True, False])
def test_archon_schema_roundtrip(fantasy_mode: bool, monkeypatch):
    payload = {
        "intent": "invoke",
        "daemon": "claude",
        "task": "Compile diagnostics",
        "safety": {"allow_shell": False, "allow_net": False},
        "style": {"fantasy": fantasy_mode, "voice": "archon"},
        "plan": ["Inspect /var/log/app.log", "Report findings"],
    }
    cleaned = validate_archon_payload(payload, fantasy_mode=fantasy_mode)
    assert cleaned["intent"] == "invoke"
    assert cleaned["daemon"] == "claude"
    if fantasy_mode:
        assert "[path-redacted]" in cleaned["plan"][0]
    else:
        assert cleaned["style"]["fantasy"] is False


def test_router_latency_budget(monkeypatch):
    router = ArchonRouter()
    router._tool_registered = True
    set_veil(True)

    async def fake_emit_route(*args, **kwargs):
        return None

    monkeypatch.setattr(router._event_bus, "emit_route", fake_emit_route)

    def fake_request(spell_text: str):
        payload: Dict[str, Any] = {
            "intent": "summon",
            "daemon": "claude",
            "task": "Summon analytics",
            "safety": {"allow_shell": False, "allow_net": False},
            "style": {"fantasy": True, "voice": "archon"},
            "plan": ["Channel spectral link"],
        }
        return payload, 0.8

    monkeypatch.setattr(router, "_request_archon_directive", fake_request)

    decision = router.analyze_spell("summon claude")
    assert decision.target_daemon.value == "liquidmetal"
    assert decision.fallback_used is True


@pytest.mark.parametrize(
    "spell, expected",
    [
        ("summon daemon of logic", "summon"),
        ("invoke scribe to draft memo", "invoke"),
        ("banish the liquid metal", "banish"),
    ],
)
def test_spell_parser_variants(spell: str, expected: str):
    router = ArchonRouter()
    router._tool_registered = False
    decision = router.analyze_spell(spell)
    assert expected in decision.intent


def test_shell_block_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(grimoire, "GRIMOIRE_FILE", tmp_path / "arcane_log.txt")
    payload = {
        "intent": "invoke",
        "daemon": "claude",
        "task": "Run shell command",
        "safety": {"allow_shell": False, "allow_net": False},
        "style": {"fantasy": True, "voice": "archon"},
        "plan": ["Open shell and execute"],
    }
    with pytest.raises(ValueError):
        validate_archon_payload(payload, fantasy_mode=True)
    log_contents = (tmp_path / "arcane_log.txt").read_text()
    assert "REJECTED_PAYLOAD" in log_contents


def test_banish_idempotent():
    daemon = daemon_registry.summon_daemon(DaemonType.CLAUDE)
    assert daemon.is_summoned is True
    daemon_registry.banish_daemon(DaemonType.CLAUDE)
    with pytest.raises(HTTPException) as excinfo:
        daemon_registry.banish_daemon(DaemonType.CLAUDE)
    assert excinfo.value.status_code == 400
