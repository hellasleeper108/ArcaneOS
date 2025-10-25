"""
The Grimoire - File-Based Memory Layer for ArcaneOS

This module provides persistent spell recording across sessions. Every spell cast,
daemon summoned, and incantation performed is recorded in the mystical grimoire
for eternal reference.

Storage Format:
- JSON Lines format (one JSON object per line)
- Each entry has timestamp, spell name, command, and result
- Integrates with Python logging for comprehensive session continuity
- Automatic pruning of old entries to prevent grimoire bloat

Functions:
- record_spell(spell_name, command, result) - Record a new spell entry
- recall_spells(limit=5) - Retrieve recent spell history
- purge_old_spells(days=30) - Remove entries older than specified days
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

# File paths for grimoire storage
GRIMOIRE_FILE = "arcane_log.txt"
SPELL_RECORDS_FILE = "grimoire_spells.jsonl"  # Dedicated spell records file


class SpellType(str, Enum):
    """Types of spells that can be recorded"""
    SUMMON = "summon"
    INVOKE = "invoke"
    BANISH = "banish"
    PARSE = "parse"
    COMPILE = "compile"
    REVEAL = "reveal"
    QUERY = "query"


class GrimoireEntry:
    """
    A single entry in the grimoire

    Each entry captures the complete context of a spell casting,
    including who cast it, what happened, and the results.
    """

    def __init__(
        self,
        spell_name: str,
        command: Dict[str, Any],
        result: Dict[str, Any],
        timestamp: Optional[float] = None,
        spell_type: Optional[str] = None,
        daemon_name: Optional[str] = None,
        success: bool = True,
        execution_time: Optional[float] = None
    ):
        self.spell_name = spell_name
        self.command = command
        self.result = result
        self.timestamp = timestamp or time.time()
        self.spell_type = spell_type
        self.daemon_name = daemon_name
        self.success = success
        self.execution_time = execution_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "spell_name": self.spell_name,
            "spell_type": self.spell_type,
            "daemon_name": self.daemon_name,
            "command": self.command,
            "result": self.result,
            "success": self.success,
            "execution_time": self.execution_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GrimoireEntry':
        """Create entry from dictionary"""
        return cls(
            spell_name=data.get("spell_name", ""),
            command=data.get("command", {}),
            result=data.get("result", {}),
            timestamp=data.get("timestamp"),
            spell_type=data.get("spell_type"),
            daemon_name=data.get("daemon_name"),
            success=data.get("success", True),
            execution_time=data.get("execution_time")
        )

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class Grimoire:
    """
    The Mystical Grimoire - Keeper of Spell History

    This class manages the persistent storage and retrieval of all spells
    cast in the ArcaneOS realm. It maintains a complete historical record
    for session continuity and arcane analysis.
    """

    def __init__(
        self,
        spell_file: str = SPELL_RECORDS_FILE,
        log_file: str = GRIMOIRE_FILE
    ):
        """
        Initialize the Grimoire

        Args:
            spell_file: Path to dedicated spell records file (JSONL)
            log_file: Path to general application log file
        """
        self.spell_file = Path(spell_file)
        self.log_file = Path(log_file)

        # Ensure spell records file exists
        if not self.spell_file.exists():
            self.spell_file.touch()
            logger.info(f"✨ Created new grimoire at {self.spell_file}")

        # Ensure log file exists
        if not self.log_file.exists():
            self.log_file.touch()
            logger.info(f"✨ Created arcane log at {self.log_file}")

    def record_spell(
        self,
        spell_name: str,
        command: Dict[str, Any],
        result: Dict[str, Any],
        spell_type: Optional[str] = None,
        daemon_name: Optional[str] = None,
        success: bool = True,
        execution_time: Optional[float] = None
    ) -> GrimoireEntry:
        """
        Record a spell in the grimoire

        This writes a JSONL entry to the dedicated spell records file and
        also logs it to the standard logger for integrated session tracking.

        Args:
            spell_name: Name of the spell cast
            command: The command/parameters of the spell
            result: The result of the spell casting
            spell_type: Type of spell (summon, invoke, etc.)
            daemon_name: Name of daemon involved (if any)
            success: Whether the spell succeeded
            execution_time: How long the spell took to execute

        Returns:
            GrimoireEntry object that was recorded
        """
        # Create entry
        entry = GrimoireEntry(
            spell_name=spell_name,
            command=command,
            result=result,
            spell_type=spell_type,
            daemon_name=daemon_name,
            success=success,
            execution_time=execution_time
        )

        # Write to spell records file (JSONL format)
        try:
            with open(self.spell_file, "a", encoding="utf-8") as f:
                f.write(entry.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to write spell to grimoire: {e}")

        # Also log to standard logger for integrated tracking
        status = "succeeded" if success else "failed"
        log_msg = (
            f"📖 SPELL RECORDED: {spell_name} {status}"
            + (f" [daemon: {daemon_name}]" if daemon_name else "")
            + (f" [time: {execution_time:.3f}s]" if execution_time else "")
        )
        logger.info(log_msg)

        return entry

    def recall_spells(
        self,
        limit: int = 5,
        spell_type: Optional[str] = None,
        daemon_name: Optional[str] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Recall recent spells from the grimoire

        Retrieves the most recent spell entries, optionally filtered by
        spell type, daemon, or success status.

        Args:
            limit: Maximum number of spells to return
            spell_type: Filter by spell type (summon, invoke, etc.)
            daemon_name: Filter by daemon name
            success_only: If True, only return successful spells

        Returns:
            List of spell entry dictionaries, most recent first
        """
        spells = []

        try:
            with open(self.spell_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        # Apply filters
                        if spell_type and entry.get("spell_type") != spell_type:
                            continue
                        if daemon_name and entry.get("daemon_name") != daemon_name:
                            continue
                        if success_only and not entry.get("success", True):
                            continue

                        spells.append(entry)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Malformed grimoire entry: {e}")
                        continue

        except FileNotFoundError:
            logger.warning("Grimoire spell file not found")
            return []

        # Return most recent spells first
        return spells[-limit:][::-1]

    def purge_old_spells(self, days: int = 30) -> int:
        """
        Purge spells older than specified days from the grimoire

        This helps prevent the grimoire from growing infinitely large.
        Archived spells are written to a backup file before deletion.

        Args:
            days: Remove spells older than this many days

        Returns:
            Number of spells purged
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        kept_spells = []
        purged_spells = []

        try:
            # Read all spells
            with open(self.spell_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        timestamp = entry.get("timestamp", 0)

                        if timestamp >= cutoff_time:
                            kept_spells.append(line)
                        else:
                            purged_spells.append(line)
                    except json.JSONDecodeError:
                        # Keep malformed entries to avoid data loss
                        kept_spells.append(line)

            # Write kept spells back
            with open(self.spell_file, "w", encoding="utf-8") as f:
                for spell in kept_spells:
                    f.write(spell + "\n")

            # Archive purged spells
            if purged_spells:
                archive_file = self.spell_file.parent / f"grimoire_archive_{int(time.time())}.jsonl"
                with open(archive_file, "w", encoding="utf-8") as f:
                    for spell in purged_spells:
                        f.write(spell + "\n")
                logger.info(f"✨ Archived {len(purged_spells)} old spells to {archive_file}")

            logger.info(f"✨ Purged {len(purged_spells)} spells older than {days} days")
            return len(purged_spells)

        except FileNotFoundError:
            logger.warning("Grimoire spell file not found")
            return 0
        except Exception as e:
            logger.error(f"Failed to purge grimoire: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the grimoire

        Returns:
            Dictionary with grimoire statistics
        """
        total_spells = 0
        spell_types = {}
        daemon_usage = {}
        success_count = 0
        fail_count = 0
        total_execution_time = 0.0
        oldest_spell = None
        newest_spell = None

        try:
            with open(self.spell_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        total_spells += 1

                        # Track spell types
                        spell_type = entry.get("spell_type", "unknown")
                        spell_types[spell_type] = spell_types.get(spell_type, 0) + 1

                        # Track daemon usage
                        daemon = entry.get("daemon_name")
                        if daemon:
                            daemon_usage[daemon] = daemon_usage.get(daemon, 0) + 1

                        # Track success/failure
                        if entry.get("success", True):
                            success_count += 1
                        else:
                            fail_count += 1

                        # Track execution time
                        exec_time = entry.get("execution_time")
                        if exec_time:
                            total_execution_time += exec_time

                        # Track timestamps
                        timestamp = entry.get("timestamp")
                        if timestamp:
                            if oldest_spell is None or timestamp < oldest_spell:
                                oldest_spell = timestamp
                            if newest_spell is None or timestamp > newest_spell:
                                newest_spell = timestamp

                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            pass

        return {
            "total_spells": total_spells,
            "spell_types": spell_types,
            "daemon_usage": daemon_usage,
            "success_count": success_count,
            "fail_count": fail_count,
            "success_rate": round(success_count / total_spells * 100, 2) if total_spells > 0 else 0,
            "total_execution_time": round(total_execution_time, 3),
            "average_execution_time": round(total_execution_time / total_spells, 3) if total_spells > 0 else 0,
            "oldest_spell": datetime.fromtimestamp(oldest_spell).isoformat() if oldest_spell else None,
            "newest_spell": datetime.fromtimestamp(newest_spell).isoformat() if newest_spell else None,
            "file_size_bytes": self.spell_file.stat().st_size if self.spell_file.exists() else 0
        }

    def search_spells(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for spells containing specific text

        Args:
            query: Search query (searches in spell_name, command, and result)
            limit: Maximum results to return

        Returns:
            List of matching spell entries
        """
        matches = []
        query_lower = query.lower()

        try:
            with open(self.spell_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        # Search in spell name, command, and result
                        searchable = json.dumps({
                            "spell_name": entry.get("spell_name", ""),
                            "command": entry.get("command", {}),
                            "result": entry.get("result", {})
                        }).lower()

                        if query_lower in searchable:
                            matches.append(entry)

                            if len(matches) >= limit:
                                break

                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            pass

        return matches[::-1]  # Most recent first


# Global singleton instance
_grimoire: Optional[Grimoire] = None


def get_grimoire() -> Grimoire:
    """
    Get the global Grimoire instance (singleton)

    Returns:
        The singleton Grimoire instance
    """
    global _grimoire

    if _grimoire is None:
        _grimoire = Grimoire()
        logger.info("✨ The Grimoire awakens, ready to record the annals of magic...")

    return _grimoire


# Legacy API functions for backward compatibility
def record_spell(spell_name: str, command: Dict[str, Any], result: Dict[str, Any]):
    """
    Records a spell in the grimoire (legacy function)

    Maintained for backward compatibility. New code should use
    get_grimoire().record_spell() for more options.
    """
    grimoire = get_grimoire()
    return grimoire.record_spell(spell_name, command, result)


def recall_spells(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recalls the last few spells from the grimoire (legacy function)

    Maintained for backward compatibility. New code should use
    get_grimoire().recall_spells() for filtering options.
    """
    grimoire = get_grimoire()
    return grimoire.recall_spells(limit=limit)


def purge_old_spells(days: int = 30) -> int:
    """
    Purges old spells from the grimoire (legacy function)

    Now actually implemented! Removes spells older than specified days.
    """
    grimoire = get_grimoire()
    return grimoire.purge_old_spells(days=days)
