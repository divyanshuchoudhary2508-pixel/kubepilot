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
    Parse a single-document YAML string safely.

    Returns (document, None) on success, or (None, YamlParseError) on failure.
    Uses safe_load since manifests should never require custom tags.
    """
    try:
        document = yaml.safe_load(content)
        return document, None
    except yaml.YAMLError as exc:
        return None, _extract_error(exc)


def parse_all_yaml(content: str) -> tuple[list[Any], Optional[YamlParseError]]:
    """
    Parse a potentially multi-document YAML string (documents separated by '---').

    Returns (documents, None) on success — documents is always a list (even for
    single-doc input). Returns ([], YamlParseError) if any document fails to parse.
    Empty documents (e.g. a bare '---' divider with nothing after it) are dropped.
    """
    try:
        # safe_load_all returns a generator; consume it fully so parse errors surface here.
        documents = [doc for doc in yaml.safe_load_all(content) if doc is not None]
        return documents, None
    except yaml.YAMLError as exc:
        return [], _extract_error(exc)


def _extract_error(exc: yaml.YAMLError) -> YamlParseError:
    line: Optional[int] = None
    mark = getattr(exc, "problem_mark", None)
    if mark is not None:
        line = mark.line + 1  # PyYAML marks are 0-indexed

    message = getattr(exc, "problem", None) or str(exc)
    return YamlParseError(line=line, message=message)
