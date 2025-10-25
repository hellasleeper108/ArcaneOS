"""
Natural Language Spell Parser for ArcaneOS.

This module provides the core functionality for parsing natural language commands
(spells) into a structured format that can be executed by the ArcaneOS daemon
registry. It uses a pattern-based approach with regular expressions to handle
various spell syntaxes for summoning, invoking, banishing, and querying daemons.

Example:
    A spell like "invoke the logic keeper to analyze my code" would be parsed into:
    {
        "action": "invoke",
        "daemon": "claude",
        "task": "analyze my code",
        "parameters": {},
        "confidence": 1.0,
        "raw_input": "invoke the logic keeper to analyze my code"
    }
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass

# Set up a dedicated logger for spell history
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='arcane_log.txt',
    filemode='a'
)
logger = logging.getLogger(__name__)


class SpellAction(str, Enum):
    """Enumeration of supported spell actions."""
    SUMMON = "summon"
    INVOKE = "invoke"
    BANISH = "banish"
    QUERY = "query"


class ParseError(Exception):
    """Custom exception raised when a spell cannot be parsed."""
    pass


@dataclass
class ParsedSpell:
    """
    A structured representation of a parsed spell command.

    This data class holds all the extracted information from a raw spell string,
    including the action to be performed, the target daemon, the task description,
    any parameters, and metadata about the parsing process.

    Attributes:
        action: The `SpellAction` to be performed.
        daemon: The canonical name of the target daemon.
        task: The description of the task for the daemon to perform.
        parameters: A dictionary of key-value parameters for the task.
        confidence: A float from 0.0 to 1.0 indicating the parser's confidence.
        raw_input: The original, unmodified spell string.
    """
    action: SpellAction
    daemon: Optional[str] = None
    task: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    raw_input: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ParsedSpell instance to a dictionary.

        Returns:
            A dictionary representation of the spell, suitable for JSON serialization.
        """
        result = {
            "action": self.action.value,
            "daemon": self.daemon,
            "confidence": self.confidence,
            "raw_input": self.raw_input,
        }
        if self.task:
            result["task"] = self.task
        if self.parameters:
            result["parameters"] = self.parameters
        return result

    def to_json(self) -> Dict[str, Any]:
        """Alias for to_dict for explicit JSON serialization contexts."""
        return self.to_dict()


class SpellPattern:
    """
    Defines a regex-based pattern for matching and parsing a specific spell syntax.

    Attributes:
        pattern: The compiled regular expression.
        action: The `SpellAction` associated with this pattern.
        groups: A mapping of attribute names (e.g., 'daemon', 'task') to their
                corresponding regex capture group index.
        priority: An integer used to determine the order in which patterns are tested.
                  Higher priority patterns are checked first.
    """

    def __init__(
        self,
        regex_pattern: str,
        action: SpellAction,
        groups: Dict[str, int],
        priority: int = 0,
    ):
        """
        Initializes a SpellPattern instance.

        Args:
            regex_pattern: The regular expression string to match against a spell.
            action: The `SpellAction` this pattern represents.
            groups: A dictionary mapping field names to regex group indices.
            priority: The priority of the pattern (higher values are checked first).
        """
        self.pattern = re.compile(regex_pattern, re.IGNORECASE)
        self.action = action
        self.groups = groups
        self.priority = priority

    def match(self, text: str) -> Optional[Dict[str, str]]:
        """
        Attempts to match the pattern against the given spell text.

        Args:
            text: The raw spell string to match.

        Returns:
            A dictionary of extracted fields if a match is found, otherwise None.
        """
        match_obj = self.pattern.search(text)
        if not match_obj:
            return None

        result = {}
        for field, group_index in self.groups.items():
            try:
                value = match_obj.group(group_index)
                if value:
                    result[field] = value.strip()
            except IndexError:
                # This can happen if a group is optional and doesn't match
                continue
        return result


class SpellParser:
    """
    A natural language parser for ArcaneOS spell commands.

    This class is responsible for taking raw text input and transforming it into
    a structured `ParsedSpell` object. It maintains a list of `SpellPattern`
    objects and tries them in order of priority to find a match.
    """

    DAEMON_ALIASES = {
        "claude": ["claude", "logic keeper", "reasoner", "analyzer"],
        "gemini": ["gemini", "creative", "innovator", "dreamer"],
        "liquidmetal": ["liquidmetal", "liquid metal", "transformer", "shapeshifter"],
    }

    ACTION_SYNONYMS = {
        SpellAction.SUMMON: [
            "summon", "call", "invoke forth", "bring forth", "materialize",
            "awaken", "raise", "conjure", "manifest",
        ],
        SpellAction.INVOKE: [
            "invoke", "ask", "request", "command", "tell", "instruct",
            "bid", "direct", "order",
        ],
        SpellAction.BANISH: [
            "banish", "dismiss", "release", "send back", "dispel",
            "vanish", "fade", "remove",
        ],
        SpellAction.QUERY: [
            "query", "check", "status", "list", "show", "display",
            "reveal", "inspect",
        ],
    }

    def __init__(self):
        """Initializes the spell parser and its pattern definitions."""
        print("INITIALIZING SPELL PARSER")
        self.patterns: List[SpellPattern] = []
        self.param_pattern = re.compile(r"with\s+(\w+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))", re.IGNORECASE)
        self._initialize_patterns()
        logger.info("SpellParser initialized with %d patterns.", len(self.patterns))

    def _initialize_patterns(self):
        """
        Defines and compiles all the regex patterns for spell parsing.
        Patterns are ordered by priority to handle ambiguity.
        """
        # INVOKE patterns (highest priority due to complexity)
        self.patterns.extend([
            SpellPattern(r"invoke\s+(\w+)\s+to\s+(.+)", SpellAction.INVOKE, {"daemon": 1, "task": 2}, priority=100),
            SpellPattern(r"ask\s+(\w+)\s+to\s+(.+)", SpellAction.INVOKE, {"daemon": 1, "task": 2}, priority=95),
            SpellPattern(r"tell\s+(\w+)\s+to\s+(.+)", SpellAction.INVOKE, {"daemon": 1, "task": 2}, priority=95),
            SpellPattern(r"command\s+(\w+):\s*(.+)", SpellAction.INVOKE, {"daemon": 1, "task": 2}, priority=90),
            SpellPattern(r"^(\w+),\s+(.+)", SpellAction.INVOKE, {"daemon": 1, "task": 2}, priority=50),
            SpellPattern(r"invoke\s+(\w+)\s+for\s+(.+)", SpellAction.INVOKE, {"daemon": 1, "task": 2}, priority=85),
        ])

        # SUMMON patterns
        self.patterns.extend([
            SpellPattern(r"summon\s+(?:the\s+)?(\w+)(?:\s+daemon)?", SpellAction.SUMMON, {"daemon": 1}, priority=80),
            SpellPattern(r"call\s+forth\s+(?:the\s+)?(\w+)", SpellAction.SUMMON, {"daemon": 1}, priority=75),
            SpellPattern(r"materialize\s+(?:the\s+)?(\w+)", SpellAction.SUMMON, {"daemon": 1}, priority=75),
            SpellPattern(r"awaken\s+(?:the\s+)?(\w+)", SpellAction.SUMMON, {"daemon": 1}, priority=75),
            SpellPattern(r"bring\s+(?:the\s+)?(\w+)\s+to\s+life", SpellAction.SUMMON, {"daemon": 1}, priority=70),
        ])

        # BANISH patterns
        self.patterns.extend([
            SpellPattern(r"banish\s+(?:the\s+)?(\w+)(?:\s+daemon)?", SpellAction.BANISH, {"daemon": 1}, priority=80),
            SpellPattern(r"dismiss\s+(?:the\s+)?(\w+)", SpellAction.BANISH, {"daemon": 1}, priority=75),
            SpellPattern(r"send\s+(?:the\s+)?(\w+)\s+back", SpellAction.BANISH, {"daemon": 1}, priority=75),
            SpellPattern(r"release\s+(?:the\s+)?(\w+)", SpellAction.BANISH, {"daemon": 1}, priority=70),
        ])

        # QUERY patterns
        self.patterns.extend([
            SpellPattern(r"^show\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?daemons?", SpellAction.QUERY, {}, priority=95),
            SpellPattern(r"^list\s+(?:all\s+)?(?:the\s+)?daemons?", SpellAction.QUERY, {}, priority=95),
            SpellPattern(r"^what\s+daemons?\s+(?:are\s+)?active", SpellAction.QUERY, {}, priority=90),
            SpellPattern(r"status\s+of\s+(?:the\s+)?(.+)", SpellAction.QUERY, {"daemon": 1}, priority=65),
            SpellPattern(r"check\s+(?:on\s+)?(?:the\s+)?(.+)", SpellAction.QUERY, {"daemon": 1}, priority=60),
        ])

        # Sort patterns by priority (descending) to ensure complex patterns are checked first
        self.patterns.sort(key=lambda p: p.priority, reverse=True)

    def normalize_daemon_name(self, raw_name: str) -> Optional[str]:
        """
        Normalizes a raw daemon name to its canonical form using aliases.

        Args:
            raw_name: The daemon name extracted from the spell text.

        Returns:
            The canonical daemon name (e.g., 'claude') or the original name if no
            alias is found.
        """
        name_lower = raw_name.lower().strip()
        for canonical_name, aliases in self.DAEMON_ALIASES.items():
            if name_lower in aliases:
                return canonical_name
        # Fallback for partial matches
        for canonical_name, aliases in self.DAEMON_ALIASES.items():
            for alias in aliases:
                if alias in name_lower or name_lower in alias:
                    return canonical_name
        return name_lower

    def extract_parameters(self, task_description: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts key-value parameters from a task description string.

        This function looks for patterns like "with key=value" and parses them
        into a dictionary. It also cleans the task description by removing the
        parameter definitions.

        Args:
            task_description: The raw task string from the spell.

        Returns:
            A tuple containing the cleaned task description and a dictionary of
            extracted parameters.
        """
        parameters = {}
        cleaned_task = task_description
        matches = self.param_pattern.finditer(task_description)

        for match in matches:
            param_name = match.group(1)
            # The value is in one of the next 3 capture groups
            param_value_str = next((g for g in match.groups()[1:] if g is not None), None)

            if param_value_str is not None:
                # Attempt to parse the value into a more specific type
                if param_value_str.lower() in ('true', 'false'):
                    param_value = param_value_str.lower() == 'true'
                elif param_value_str.isdigit():
                    param_value = int(param_value_str)
                else:
                    try:
                        param_value = float(param_value_str)
                    except ValueError:
                        param_value = param_value_str  # Keep as string
                parameters[param_name] = param_value

                # Remove the parameter string from the task
                cleaned_task = cleaned_task.replace(match.group(0), '').strip()

        # Remove extra whitespace and trailing punctuation
        cleaned_task = re.sub(r'\s+', ' ', cleaned_task).strip(' ,;')
        return cleaned_task, parameters

    def parse(self, spell_text: str) -> ParsedSpell:
        """
        Parses a natural language spell into a structured ParsedSpell object.

        Args:
            spell_text: The raw natural language spell command.

        Returns:
            A `ParsedSpell` object containing the structured command.

        Raises:
            ParseError: If the spell text is empty or cannot be matched to any pattern.
        """
        if not spell_text or not spell_text.strip():
            raise ParseError("Empty spell text provided.")

        cleaned_spell_text = spell_text.strip()
        logger.info("Parsing spell: '%s'", cleaned_spell_text)

        for pattern in self.patterns:
            matched_fields = pattern.match(cleaned_spell_text)
            if matched_fields is not None:
                daemon_name = None
                if "daemon" in matched_fields:
                    daemon_name = self.normalize_daemon_name(matched_fields["daemon"])

                task_description = None
                task_parameters = None
                if "task" in matched_fields:
                    raw_task = matched_fields["task"]
                    task_description, task_parameters = self.extract_parameters(raw_task)

                confidence = min(1.0, pattern.priority / 100.0)

                parsed_spell = ParsedSpell(
                    action=pattern.action,
                    daemon=daemon_name,
                    task=task_description,
                    parameters=task_parameters,
                    confidence=confidence,
                    raw_input=cleaned_spell_text,
                )
                logger.info("Successfully parsed spell: %s", parsed_spell.to_dict())
                return parsed_spell

        logger.warning("Failed to parse spell: '%s'", cleaned_spell_text)
        raise ParseError(
            f"Unable to parse spell: '{cleaned_spell_text}'. "
            "Try commands like: 'summon claude', 'invoke gemini to create art', "
            "or 'banish liquidmetal'."
        )

    def parse_batch(self, spell_texts: List[str]) -> List[ParsedSpell]:
        """
        Parses a list of spell commands in a batch.

        Args:
            spell_texts: A list of raw spell command strings.

        Returns:
            A list of `ParsedSpell` objects. Invalid spells are skipped.
        """
        results = []
        for spell_text in spell_texts:
            try:
                parsed = self.parse(spell_text)
                results.append(parsed)
            except ParseError:
                # In batch mode, we skip spells that fail to parse.
                continue
        return results

    def suggest_correction(self, failed_spell_text: str) -> List[str]:
        """
        Provides suggestions for correcting a spell that failed to parse.

        Args:
            failed_spell_text: The spell string that could not be parsed.

        Returns:
            A list of human-readable suggestions for how to correct the spell.
        """
        suggestions = []
        text_lower = failed_spell_text.lower()

        # Check for the presence of an action keyword
        has_action = any(
            syn in text_lower
            for synonyms in self.ACTION_SYNONYMS.values()
            for syn in synonyms
        )
        if not has_action:
            suggestions.append("Try starting with an action like 'summon', 'invoke', or 'banish'.")

        # Check for the presence of a daemon name
        has_daemon = any(
            alias in text_lower
            for aliases in self.DAEMON_ALIASES.values()
            for alias in aliases
        )
        if not has_daemon:
            suggestions.append(f"Include a known daemon name: {', '.join(self.DAEMON_ALIASES.keys())}.")

        # Provide concrete examples
        suggestions.extend([
            "Example: 'invoke claude to analyze code'",
            "Example: 'summon gemini'",
            "Example: 'banish liquidmetal'",
        ])
        return suggestions


# Singleton instance of the SpellParser
_spell_parser: Optional[SpellParser] = None


def get_spell_parser() -> SpellParser:
    """

    Provides access to the global singleton instance of the SpellParser.

    This factory function ensures that only one instance of the SpellParser is
    created and used throughout the application, which is efficient as the
    patterns only need to be compiled once.

    Returns:
        The singleton `SpellParser` instance.
    """
    global _spell_parser
    if _spell_parser is None:
        _spell_parser = SpellParser()
    return _spell_parser