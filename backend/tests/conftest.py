"""
Shared fixtures and helpers for the KubePilot test suite.
"""
import textwrap
import pytest


def dedent(text: str) -> str:
    """Strip leading newline and common indentation from inline YAML fixtures."""
    return textwrap.dedent(text).lstrip("\n")
