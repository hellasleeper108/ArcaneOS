"""
Enhanced Daemon Registry Service for ArcaneOS

Manages the mystical registry of daemons with full Raindrop MCP integration.
This service maintains the ethereal connection between the mortal realm and daemon entities,
routing all invocations through the Raindrop MCP interface.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime
from app.models.daemon import Daemon, DaemonType, DaemonRole
from app.services.raindrop_client import (
    get_mcp_client,
    ModelProvider,
    MCPToolResult
)
from app.services.arcane_event_bus import get_event_bus
from app.services.daemon_voice import get_daemon_voice_service, VoiceEvent
from app.services.grimoire import get_grimoire
from fastapi import HTTPException
import logging
import asyncio

logger = logging.getLogger(__name__)


def _safe_create_task(coro):
    """
    Safely create an async task only if an event loop is running.
    This allows the daemon registry to work in both async (production)
    and sync (test) contexts without raising RuntimeError.

    Args:
        coro: The coroutine to run as a task
    """
    try:
        loop = asyncio.get_running_loop()
        _safe_create_task(coro)
    except RuntimeError:
        # No event loop running - likely in test context
        # Log and continue without executing the async task
        logger.debug("No event loop running - skipping async task creation")


class DaemonState:
    """
    Tracks the active state of a daemon including invocation history
    """

    def __init__(self, daemon: Daemon):
        self.daemon = daemon
        self.summoned_at: Optional[datetime] = None
        self.last_invoked_at: Optional[datetime] = None
        self.invocation_history: List[Dict[str, Any]] = []
        self.total_execution_time: float = 0.0
        self.mcp_registered: bool = False

    def record_invocation(
        self,
        task: str,
        result: MCPToolResult
    ):
        """Record an invocation in the daemon's history"""
        self.last_invoked_at = datetime.utcnow()
        self.total_execution_time += result.execution_time

        self.invocation_history.append({
            "task": task,
            "timestamp": result.timestamp.isoformat(),
            "execution_time": result.execution_time,
            "success": result.success,
            "result_summary": str(result.result)[:200]  # Truncate for storage
        })

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about this daemon's activity"""
        return {
            "daemon_name": self.daemon.name.value,
            "is_active": self.daemon.is_summoned,
            "summoned_at": self.summoned_at.isoformat() if self.summoned_at else None,
            "last_invoked_at": self.last_invoked_at.isoformat() if self.last_invoked_at else None,
            "total_invocations": len(self.invocation_history),
            "total_execution_time": round(self.total_execution_time, 3),
            "average_execution_time": (
                round(self.total_execution_time / len(self.invocation_history), 3)
                if self.invocation_history else 0.0
            ),
            "mcp_registered": self.mcp_registered
        }


class DaemonRegistry:
    """
    Enhanced Grimoire of Daemons - a mystical registry with Raindrop MCP integration

    This registry manages daemon lifecycles and routes all invocations through
    the Raindrop MCP interface for proper model routing.
    """

    # Model mappings for each daemon
    MODEL_MAPPINGS = {
        DaemonType.CLAUDE: {
            "model": "claude-3-5-sonnet-20241022",
            "provider": ModelProvider.ANTHROPIC,
            "capabilities": ["reasoning", "analysis", "code_generation", "logic"]
        },
        DaemonType.GEMINI: {
            "model": "gemini-2.0-flash-exp",
            "provider": ModelProvider.GOOGLE,
            "capabilities": ["creativity", "multimodal", "vision", "innovation"]
        },
        DaemonType.LIQUIDMETAL: {
            "model": "liquidmetal-adaptive-v1",
            "provider": ModelProvider.CUSTOM,
            "capabilities": ["transformation", "adaptation", "flow", "custom_tasks"]
        }
    }

    def __init__(self):
        """Initialize the enhanced daemon registry with MCP integration"""
        self._daemons: Dict[DaemonType, Daemon] = {}
        self._daemon_states: Dict[DaemonType, DaemonState] = {}
        self._mcp_client = get_mcp_client()
        self._voice_service = get_daemon_voice_service()

        # Initialize the three primary daemon archetypes
        self._initialize_daemons()

        logger.info("Enhanced DaemonRegistry initialized with MCP integration")

    def _initialize_daemons(self):
        """
        Inscribe the three primary daemons into the grimoire.
        They exist in potential, waiting to be summoned and registered.
        """
        daemon_configurations = {
            DaemonType.CLAUDE: {
                "name": DaemonType.CLAUDE,
                "role": DaemonRole.LOGIC.value,
                "color_code": "#8B5CF6",  # Mystical purple
                "metadata": {
                    "element": "Aether",
                    "domain": "Reasoning and Analysis",
                    "power_level": 9000,
                    "model": self.MODEL_MAPPINGS[DaemonType.CLAUDE]["model"]
                }
            },
            DaemonType.GEMINI: {
                "name": DaemonType.GEMINI,
                "role": DaemonRole.CREATIVITY.value,
                "color_code": "#F59E0B",  # Golden amber
                "metadata": {
                    "element": "Fire",
                    "domain": "Creativity and Multimodality",
                    "power_level": 8500,
                    "model": self.MODEL_MAPPINGS[DaemonType.GEMINI]["model"]
                }
            },
            DaemonType.LIQUIDMETAL: {
                "name": DaemonType.LIQUIDMETAL,
                "role": DaemonRole.ALCHEMY.value,
                "color_code": "#06B6D4",  # Liquid cyan
                "metadata": {
                    "element": "Water",
                    "domain": "Transformation and Adaptation",
                    "power_level": 9500,
                    "model": self.MODEL_MAPPINGS[DaemonType.LIQUIDMETAL]["model"]
                }
            }
        }

        for daemon_type, config in daemon_configurations.items():
            daemon = Daemon(**config)
            self._daemons[daemon_type] = daemon
            self._daemon_states[daemon_type] = DaemonState(daemon)

    def register_daemon(
        self,
        name: DaemonType,
        model: str,
        role: str,
        color_code: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Daemon:
        """
        Register a daemon with the Raindrop MCP interface

        This method registers a daemon as an MCP tool, enabling it to be
        invoked through the Raindrop routing system.

        Args:
            name: The daemon's true name (DaemonType)
            model: The AI model to use (e.g., "claude-3-5-sonnet")
            role: The mystical role this daemon fulfills
            color_code: Optional color code override
            capabilities: Optional list of capabilities override

        Returns:
            The registered daemon entity

        Raises:
            HTTPException: If daemon doesn't exist or registration fails
        """
        if name not in self._daemons:
            raise HTTPException(
                status_code=404,
                detail=f"The daemon '{name}' is unknown to this realm"
            )

        daemon = self._daemons[name]
        state = self._daemon_states[name]

        # Update daemon configuration if provided
        if color_code:
            daemon.color_code = color_code
        if role:
            daemon.role = role

        # Update model in metadata
        if daemon.metadata:
            daemon.metadata["model"] = model
        else:
            daemon.metadata = {"model": model}

        # Get capabilities from mapping or use provided
        model_config = self.MODEL_MAPPINGS.get(name, {})
        tool_capabilities = capabilities or model_config.get("capabilities", [])
        provider = model_config.get("provider", ModelProvider.CUSTOM)

        # Register with MCP
        success = self._mcp_client.register_tool(
            tool_name=name.value,
            model=model,
            provider=provider,
            capabilities=tool_capabilities,
            metadata={
                "role": daemon.role,
                "color_code": daemon.color_code,
                "daemon_metadata": daemon.metadata
            }
        )

        if success:
            state.mcp_registered = True
            logger.info(
                f"Daemon '{name.value}' registered with MCP using model '{model}'"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to register daemon '{name}' with Raindrop MCP"
            )

        return daemon

    def summon(self, daemon_name: DaemonType) -> Daemon:
        """
        Summon a daemon into the material realm and register with MCP

        Args:
            daemon_name: The true name of the daemon to summon

        Returns:
            The summoned daemon entity

        Raises:
            HTTPException: If the daemon is already summoned or doesn't exist
        """
        event_bus = get_event_bus()

        try:
            if daemon_name not in self._daemons:
                raise HTTPException(
                    status_code=404,
                    detail=f"The daemon '{daemon_name}' is unknown to this realm"
                )

            daemon = self._daemons[daemon_name]
            state = self._daemon_states[daemon_name]

            if daemon.is_summoned:
                raise HTTPException(
                    status_code=400,
                    detail=f"The daemon {daemon_name} already walks among us"
                )

            # Perform the summoning ritual
            daemon.is_summoned = True
            daemon.invocation_count = 0
            state.summoned_at = datetime.utcnow()

            # Auto-register with MCP if not already registered
            if not state.mcp_registered:
                model_config = self.MODEL_MAPPINGS.get(daemon_name, {})
                if model_config:
                    self.register_daemon(
                        name=daemon_name,
                        model=model_config["model"],
                        role=daemon.role,
                        capabilities=model_config.get("capabilities")
                    )
            else:
                model_config = self.MODEL_MAPPINGS.get(daemon_name, {})

            logger.info(f"Daemon '{daemon_name.value}' summoned successfully")

            # Emit summon event (async, run in background)
            metadata = {
                "model": model_config.get("model") if model_config else None,
                "sync_context": "summon"
            }
            _safe_create_task(event_bus.emit_summon(
                daemon_name=daemon_name.value,
                success=True,
                metadata=metadata
            ))

            _safe_create_task(self._voice_service.play_voice_line(
                daemon=daemon_name,
                event=VoiceEvent.SUMMON
            ))

            # Record in grimoire
            grimoire = get_grimoire()
            grimoire.record_spell(
                spell_name=f"summon_{daemon_name.value}",
                command={"daemon_name": daemon_name.value},
                result={"status": "summoned", "daemon": daemon.name.value},
                spell_type="summon",
                daemon_name=daemon_name.value,
                success=True
            )

            return daemon

        except HTTPException as exc:
            failure_phrase = (
                f"The summoning of {daemon_name.value} falters: {exc.detail}"
            )
            failure_metadata = {
                "error": exc.detail,
                "failure_phrase": failure_phrase,
                "sync_context": "summon"
            }
            _safe_create_task(event_bus.emit_summon(
                daemon_name=daemon_name.value,
                success=False,
                metadata=failure_metadata
            ))
            _safe_create_task(self._voice_service.play_voice_line(
                daemon=daemon_name,
                event=VoiceEvent.FAILURE,
                override_text=failure_phrase
            ))
            raise

        except Exception as exc:
            failure_phrase = (
                f"Unseen forces disrupt {daemon_name.value}: {exc}"
            )
            failure_metadata = {
                "error": str(exc),
                "failure_phrase": failure_phrase,
                "sync_context": "summon"
            }
            _safe_create_task(event_bus.emit_summon(
                daemon_name=daemon_name.value,
                success=False,
                metadata=failure_metadata
            ))
            _safe_create_task(self._voice_service.play_voice_line(
                daemon=daemon_name,
                event=VoiceEvent.FAILURE,
                override_text=failure_phrase
            ))
            raise

    # Legacy compatibility helpers -------------------------------------------------

    def summon_daemon(self, name: DaemonType) -> Daemon:
        """Legacy summon method for backward compatibility"""
        return self.summon(name)

    def invoke_daemon(
        self,
        name: DaemonType,
        task: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a daemon's power through the Raindrop MCP interface

        This method routes the invocation through Raindrop MCP, ensuring
        the appropriate AI model handles the task.

        Args:
            name: The true name of the daemon to invoke
            task: The mystical task to request of the daemon
            parameters: Optional additional parameters for the invocation

        Returns:
            Dictionary containing the invocation result and metadata

        Raises:
            HTTPException: If the daemon hasn't been summoned or doesn't exist
        """
        event_bus = get_event_bus()

        try:
            if name not in self._daemons:
                raise HTTPException(
                    status_code=404,
                    detail=f"The daemon '{name}' is unknown to this realm"
                )

            daemon = self._daemons[name]
            state = self._daemon_states[name]

            if not daemon.is_summoned:
                raise HTTPException(
                    status_code=400,
                    detail=f"The daemon {name} slumbers in the void. Summon it first."
                )

            if not state.mcp_registered:
                raise HTTPException(
                    status_code=500,
                    detail=f"The daemon {name} is not registered with MCP. "
                           "This should not happen - try re-summoning."
                )

            # Invoke through Raindrop MCP
            result: MCPToolResult = self._mcp_client.invoke_tool(
                tool_name=name.value,
                task=task,
                parameters=parameters
            )

            # Update daemon state
            daemon.invocation_count += 1
            state.record_invocation(task, result)

            logger.info(
                f"Daemon '{name.value}' invoked successfully "
                f"(execution time: {result.execution_time}s)"
            )

            # Emit invoke event (async, run in background)
            success_flag = bool(result.success)
            metadata = {
                "parameters": parameters,
                "invocation_number": daemon.invocation_count,
                "sync_context": "invoke"
            }

            if success_flag:
                metadata["success_payload"] = result.result
                _safe_create_task(self._voice_service.play_voice_line(
                    daemon=name,
                    event=VoiceEvent.INVOKE
                ))
            else:
                failure_phrase = (
                    f"{name.value} reports failure while invoking '{task}'"
                )
                metadata["error"] = result.result
                metadata["failure_phrase"] = failure_phrase
                _safe_create_task(self._voice_service.play_voice_line(
                    daemon=name,
                    event=VoiceEvent.FAILURE,
                    override_text=failure_phrase
                ))

            _safe_create_task(event_bus.emit_invoke(
                daemon_name=name.value,
                task=task,
                success=success_flag,
                execution_time=result.execution_time,
                metadata=metadata
            ))

            # Record in grimoire
            grimoire = get_grimoire()
            grimoire.record_spell(
                spell_name=f"invoke_{name.value}",
                command={"daemon_name": name.value, "task": task, "parameters": parameters},
                result={"output": result.result, "success": result.success},
                spell_type="invoke",
                daemon_name=name.value,
                success=result.success,
                execution_time=result.execution_time
            )

            return {
                "daemon": daemon,
                "result": result.result,
                "execution_time": result.execution_time,
                "success": result.success,
                "metadata": result.metadata,
                "invocation_number": daemon.invocation_count
            }

        except HTTPException as exc:
            failure_phrase = (
                f"Invocation of {name.value} falters: {exc.detail}"
            )
            failure_metadata = {
                "error": exc.detail,
                "failure_phrase": failure_phrase,
                "task": task,
                "sync_context": "invoke"
            }
            _safe_create_task(event_bus.emit_invoke(
                daemon_name=name.value,
                task=task,
                success=False,
                metadata=failure_metadata
            ))
            _safe_create_task(self._voice_service.play_voice_line(
                daemon=name,
                event=VoiceEvent.FAILURE,
                override_text=failure_phrase
            ))
            raise

        except Exception as exc:
            logger.error(f"Failed to invoke daemon '{name.value}': {exc}")
            failure_phrase = (
                f"Arcane backlash disrupts {name.value}: {exc}"
            )
            failure_metadata = {
                "error": str(exc),
                "failure_phrase": failure_phrase,
                "task": task,
                "sync_context": "invoke"
            }
            _safe_create_task(event_bus.emit_invoke(
                daemon_name=name.value,
                task=task,
                success=False,
                metadata=failure_metadata
            ))
            _safe_create_task(self._voice_service.play_voice_line(
                daemon=name,
                event=VoiceEvent.FAILURE,
                override_text=failure_phrase
            ))
            raise HTTPException(
                status_code=500,
                detail=f"Invocation failed: {str(exc)}"
            )

    # Alias for compatibility
    def invoke(self, daemon_name: DaemonType, task: str) -> Daemon:
        """Legacy invoke method for backward compatibility"""
        result = self.invoke_daemon(daemon_name, task)
        return result["daemon"]

    def banish_daemon(self, name: DaemonType) -> Dict[str, Any]:
        """
        Banish a daemon back to the ethereal realm with proper cleanup

        This method unregisters the daemon from MCP and resets its state.

        Args:
            name: The true name of the daemon to banish

        Returns:
            Dictionary containing banishment details and statistics

        Raises:
            HTTPException: If the daemon isn't summoned or doesn't exist
        """
        event_bus = get_event_bus()

        try:
            if name not in self._daemons:
                raise HTTPException(
                    status_code=404,
                    detail=f"The daemon '{name}' is unknown to this realm"
                )

            daemon = self._daemons[name]
            state = self._daemon_states[name]

            if not daemon.is_summoned:
                raise HTTPException(
                    status_code=400,
                    detail=f"The daemon {name} is not present in this realm"
                )

            # Collect statistics before banishment
            statistics = state.get_statistics()

            # Unregister from MCP
            if state.mcp_registered:
                self._mcp_client.unregister_tool(name.value)
                state.mcp_registered = False

            # Perform the banishment ritual
            daemon.is_summoned = False

            logger.info(
                f"Daemon '{name.value}' banished after {len(state.invocation_history)} "
                f"invocation(s)"
            )

            # Emit banish event (async, run in background)
            metadata = statistics.copy()
            metadata["sync_context"] = "banish"
            _safe_create_task(event_bus.emit_banish(
                daemon_name=name.value,
                invocation_count=statistics['total_invocations'],
                total_time=statistics['total_execution_time'],
                success=True,
                metadata=metadata
            ))

            _safe_create_task(self._voice_service.play_voice_line(
                daemon=name,
                event=VoiceEvent.BANISH
            ))

            # Record in grimoire
            grimoire = get_grimoire()
            grimoire.record_spell(
                spell_name=f"banish_{name.value}",
                command={"daemon_name": name.value},
                result={"status": "banished", "statistics": statistics},
                spell_type="banish",
                daemon_name=name.value,
                success=True,
                execution_time=statistics.get('total_execution_time')
            )

            return {
                "daemon": daemon,
                "statistics": statistics,
                "message": f"✨ The daemon {name.value} returns to the ether, its energies dispersed. ✨"
            }

        except HTTPException as exc:
            failure_phrase = (
                f"Banishment of {name.value} fails: {exc.detail}"
            )
            failure_metadata = {
                "error": exc.detail,
                "failure_phrase": failure_phrase,
                "sync_context": "banish"
            }
            _safe_create_task(event_bus.emit_banish(
                daemon_name=name.value,
                invocation_count=0,
                total_time=0.0,
                success=False,
                metadata=failure_metadata
            ))
            _safe_create_task(self._voice_service.play_voice_line(
                daemon=name,
                event=VoiceEvent.FAILURE,
                override_text=failure_phrase
            ))
            raise

        except Exception as exc:
            failure_phrase = (
                f"A banishment backlash surrounds {name.value}: {exc}"
            )
            failure_metadata = {
                "error": str(exc),
                "failure_phrase": failure_phrase,
                "sync_context": "banish"
            }
            _safe_create_task(event_bus.emit_banish(
                daemon_name=name.value,
                invocation_count=0,
                total_time=0.0,
                success=False,
                metadata=failure_metadata
            ))
            _safe_create_task(self._voice_service.play_voice_line(
                daemon=name,
                event=VoiceEvent.FAILURE,
                override_text=failure_phrase
            ))
            raise

    # Alias for compatibility
    def banish(self, daemon_name: DaemonType) -> Daemon:
        """Legacy banish method for backward compatibility"""
        result = self.banish_daemon(daemon_name)
        return result["daemon"]

    def get_daemon(self, daemon_name: DaemonType) -> Optional[Daemon]:
        """Retrieve a daemon's information from the registry"""
        return self._daemons.get(daemon_name)

    def get_daemon_state(self, daemon_name: DaemonType) -> Optional[DaemonState]:
        """Retrieve a daemon's state information"""
        return self._daemon_states.get(daemon_name)

    def get_all_daemons(self) -> Dict[DaemonType, Daemon]:
        """Retrieve all daemons from the registry"""
        return self._daemons.copy()

    def get_active_daemons(self) -> Dict[DaemonType, Daemon]:
        """Retrieve only currently summoned (active) daemons"""
        return {
            name: daemon
            for name, daemon in self._daemons.items()
            if daemon.is_summoned
        }

    def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the entire registry

        Returns:
            Dictionary containing registry-wide statistics
        """
        active_count = sum(1 for d in self._daemons.values() if d.is_summoned)
        total_invocations = sum(
            len(state.invocation_history)
            for state in self._daemon_states.values()
        )

        daemon_stats = {
            name.value: state.get_statistics()
            for name, state in self._daemon_states.items()
        }

        return {
            "total_daemons": len(self._daemons),
            "active_daemons": active_count,
            "dormant_daemons": len(self._daemons) - active_count,
            "total_invocations": total_invocations,
            "mcp_registered_daemons": sum(
                1 for s in self._daemon_states.values() if s.mcp_registered
            ),
            "daemon_statistics": daemon_stats
        }


# Global registry instance (in production, this would use proper dependency injection)
daemon_registry = DaemonRegistry()
