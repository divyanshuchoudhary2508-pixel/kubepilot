"""
yaml.safe_load() gives us plain dicts/lists with no position info, which is
fine for reading values but useless for reporting line numbers back to the
user. yaml.compose() gives us the underlying Node tree, which *does* carry
start_mark.line for every node. This module bridges the two: callers pass a
"path" (e.g. ["spec", "selector"] or ["spec", "template", "spec",
"containers", 0]) and get back the best line number we can find for it.
"""

from __future__ import annotations

from typing import Optional, Union

import yaml

PathSegment = Union[str, int]


def get_line(content: str, path: list[PathSegment]) -> Optional[int]:
    """
    Walk the composed YAML node tree along `path` and return the 1-indexed
    line number of the deepest node reached. If the full path doesn't exist,
    returns the line of the deepest ancestor that does (useful for pointing
    at "where this missing field should go"). Returns None only if even the
    document root can't be composed (e.g. invalid YAML).
    """
    try:
        node = yaml.compose(content)
    except yaml.YAMLError:
        return None

    if node is None:
        return None

    best_line = node.start_mark.line + 1

    for segment in path:
        if isinstance(segment, int):
            if not isinstance(node, yaml.SequenceNode) or segment >= len(node.value):
                break
            node = node.value[segment]
        else:
            if not isinstance(node, yaml.MappingNode):
                break
            match = next((v for k, v in node.value if k.value == segment), None)
            if match is None:
                break
            node = match

        best_line = node.start_mark.line + 1

    return best_line
