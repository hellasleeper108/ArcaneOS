"""
Spell Parser API Routes for ArcaneOS.

This module defines the FastAPI routes for parsing and executing natural language
spells. It provides endpoints for parsing single spells, batch parsing, and
directly casting a spell to be executed by the daemon registry.

Endpoints:
    - POST /spell/parse: Parses a single spell into a structured command.
    - POST /spell/parse-batch: Parses a list of spells simultaneously.
    - GET /spell/examples: Returns a list of example spell commands.
    - POST /spell/cast: Parses and immediately executes a spell.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List

from app.config import settings
from app.models.daemon import SpellParseRequest, ParsedSpellResponse
from app.services.archon_router import get_archon_router
from app.services.grimoire import record_spell, recall_spells
from ArcaneOS.core.veil import is_fantasy_mode

# Create a new router for spell-related endpoints
router = APIRouter(
    prefix="/spell",
    tags=["Spell Parser"],
    responses={400: {"description": "Invalid or unparseable spell format"}},
)


@router.post("/parse", response_model=ParsedSpellResponse)
async def parse_spell_endpoint(request: SpellParseRequest):
    """
    🔮 Parse a Single Spell 🔮

    Translates a natural language spell command into a structured JSON format.
    This endpoint is the primary way to interpret a user's intent without
    executing it. It provides detailed information about the parsed command,
    including the action, daemon, task, and any parameters.

    If parsing fails, it returns suggestions for how to correct the spell.

    Args:
        request: A `SpellParseRequest` object containing the raw spell string.

    Returns:
        A `ParsedSpellResponse` object with the structured spell data or an error.
    """
    archon = get_archon_router()

    try:
        decision = archon.analyze_spell(request.spell)
        summary = decision.parsed_summary or {}
        fantasy = is_fantasy_mode()

        return ParsedSpellResponse(
            success=True,
            action=summary.get("action"),
            daemon=summary.get("daemon"),
            task=summary.get("task"),
            parameters=summary.get("parameters"),
            confidence=decision.confidence,
            raw_input=summary.get("raw_input", request.spell),
            error=None,
            suggestions=None,
            archon_narration=decision.narration if fantasy else decision.reasoning,
            archon_reasoning=decision.reasoning,
            archon_fallback_used=decision.fallback_used,
            archon_chain_of_thought=decision.chain_of_thought or None,
            archon_confidence=decision.confidence,
            archon_raw_decision=decision.raw or None,
        )
    except HTTPException as exc:
        fantasy = is_fantasy_mode()
        return ParsedSpellResponse(
            success=False,
            action=None,
            daemon=None,
            task=None,
            parameters=None,
            confidence=None,
            raw_input=request.spell,
            error=str(exc.detail),
            suggestions=None,
            archon_narration=(
                f"{settings.archon_role_name} hesitates, unable to decipher the spell."
                if fantasy
                else "spell_parser_error"
            ),
            archon_reasoning=str(exc.detail),
            archon_fallback_used=True,
            archon_chain_of_thought=None,
            archon_confidence=None,
            archon_raw_decision=None,
        )


@router.post("/parse-batch", response_model=List[ParsedSpellResponse])
async def parse_spell_batch_endpoint(spells: List[str] = Body(..., embed=True)):
    """
    🔮 Batch Parse Multiple Spells 🔮

    Parses a list of natural language spell commands in a single request.
    This is more efficient than calling the `/parse` endpoint multiple times.

    Args:
        spells: A list of raw spell strings to be parsed.

    Returns:
        A list of `ParsedSpellResponse` objects, one for each spell.
    """
    responses = []
    archon = get_archon_router()

    for spell_text in spells:
        try:
            decision = archon.analyze_spell(spell_text)
            summary = decision.parsed_summary or {}
            fantasy = is_fantasy_mode()
            responses.append(
                ParsedSpellResponse(
                    success=True,
                    action=summary.get("action"),
                    daemon=summary.get("daemon"),
                    task=summary.get("task"),
                    parameters=summary.get("parameters"),
                    confidence=decision.confidence,
                    raw_input=summary.get("raw_input", spell_text),
                    error=None,
                    suggestions=None,
                    archon_narration=decision.narration if fantasy else decision.reasoning,
                    archon_reasoning=decision.reasoning,
                    archon_fallback_used=decision.fallback_used,
                    archon_chain_of_thought=decision.chain_of_thought or None,
                    archon_confidence=decision.confidence,
                    archon_raw_decision=decision.raw or None,
                )
            )
        except HTTPException as exc:
            responses.append(
                ParsedSpellResponse(
                    success=False,
                    action=None,
                    daemon=None,
                    task=None,
                    parameters=None,
                    confidence=None,
                    raw_input=spell_text,
                    error=str(exc.detail),
                    suggestions=None,
                    archon_narration=(
                        f"{settings.archon_role_name} hesitates, unable to decipher the spell."
                        if is_fantasy_mode()
                        else "spell_parser_error"
                    ),
                    archon_reasoning=str(exc.detail),
                    archon_fallback_used=True,
                    archon_chain_of_thought=None,
                    archon_confidence=None,
                    archon_raw_decision=None,
                )
            )
    return responses


@router.get("/examples")
async def get_spell_examples_endpoint():
    """
    📜 Retrieve Spell Examples 📜

    Provides a list of example spell incantations to help users learn the
    correct syntax for interacting with ArcaneOS.

    Returns:
        A dictionary of example spells, categorized by action type.
    """
    return {
        "summon_examples": [
            "summon claude",
            "call forth the gemini daemon",
            "materialize liquidmetal",
        ],
        "invoke_examples": [
            "invoke claude to analyze this code",
            "ask gemini to create a logo with style=vintage",
            "tell liquidmetal to transform data",
        ],
        "banish_examples": [
            "banish claude",
            "dismiss the gemini daemon",
            "send liquidmetal back",
        ],
        "query_examples": [
            "show me all daemons",
            "list active daemons",
            "status of claude",
        ],
    }


@router.post("/cast")
async def cast_spell_endpoint(request: SpellParseRequest):
    """
    ⚡ Cast and Execute a Spell ⚡

    Routes a natural language spell through The Archon, executing the resulting
    daemon action and returning a narrated outcome.
    """
    archon = get_archon_router()

    try:
        decision = archon.analyze_spell(request.spell)
        execution = archon.execute_decision(decision)
        fantasy = is_fantasy_mode()

        response = {
            "success": True,
            "archon": {
                "role": settings.archon_role_name,
                "narration": decision.narration if fantasy else decision.reasoning,
                "reasoning": decision.reasoning,
                "fallback_used": decision.fallback_used,
                "fallback_strategy": decision.fallback_strategy,
                "chain_of_thought": decision.chain_of_thought,
                "confidence": decision.confidence,
                "raw_decision": decision.raw,
                **({"dev_mode": True} if not fantasy else {}),
            },
            "parsed": decision.parsed_summary,
            "execution": execution,
        }

        record_spell(request.spell, decision.parsed_summary, response)
        return response

    except HTTPException as exc:
        # Attempt to recover decision context to deliver a helpful response
        try:
            decision = archon.analyze_spell(request.spell)
        except HTTPException:
            decision = None

        failure_response = {
            "success": False,
            "error": str(exc.detail),
            "archon": {
                "role": settings.archon_role_name,
                "narration": decision.narration if decision else f"{settings.archon_role_name} falters mid-ritual.",
                "reasoning": decision.reasoning if decision else str(exc.detail),
                "fallback_used": decision.fallback_used if decision else True,
                "fallback_strategy": decision.fallback_strategy if decision else "parser",
                "chain_of_thought": decision.chain_of_thought if decision else None,
                "confidence": decision.confidence if decision else None,
                "raw_decision": decision.raw if decision else None,
            },
            "parsed": decision.parsed_summary if decision else None,
        }

        record_spell(request.spell, decision.parsed_summary if decision else {}, failure_response)
        return failure_response

@router.get("/grimoire/recall")
async def recall_spells_endpoint(limit: int = 5):
    """
    📖 Recall Spells from the Grimoire 📖

    Recalls the last few spells cast in the realm, showing their names,
    the commands given, and the results.

    Args:
        limit: The number of spells to recall.

    Returns:
        A list of the last few spells cast.
    """
    return recall_spells(limit)
