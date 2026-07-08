"""
Thin wrapper around PyYAML that turns parse errors into structured
(line, message) data instead of raw exception text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import yaml


@dataclass
class YamlParseError:
    line: Optional[int]
    message: str


def parse_yaml(content: str) -> tuple[Optional[Any], Optional[YamlParseError]]:
    """
    Parse YAML content safely.

    Returns (document, None) on success, or (None, YamlParseError) on failure.
    Uses safe_load since manifests should never require custom tags.
    """
    try:
        document = yaml.safe_load(content)
        return document, None
    except yaml.YAMLError as exc:
        line: Optional[int] = None
        mark = getattr(exc, "problem_mark", None)
        if mark is not None:
            line = mark.line + 1  # PyYAML marks are 0-indexed

        message = getattr(exc, "problem", None) or str(exc)
        return None, YamlParseError(line=line, message=message)
