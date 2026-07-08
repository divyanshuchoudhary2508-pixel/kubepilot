"""
Deterministic (non-AI) fixer. Loads the manifest with ruamel.yaml's
round-trip loader so existing comments/formatting/key order survive, applies
a small fixed set of patches, and dumps the result back to text.

Only fixes with an unambiguous, mechanical answer are applied:
  - spec.replicas missing              -> replicas: 1
  - spec.selector.matchLabels missing  -> copied from template.metadata.labels
  - metadata.labels missing            -> derived from metadata.name
  - container resources.requests/limits missing -> reasonable static defaults
  - Service spec.type missing          -> "ClusterIP" (Kubernetes' own default)

Anything that would require guessing the user's intent — a container's name,
its image, probe paths, port numbers — is intentionally left alone and stays
flagged by /validate instead.
"""

from __future__ import annotations

from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

DEFAULT_REQUESTS = {"cpu": "100m", "memory": "128Mi"}
DEFAULT_LIMITS = {"cpu": "500m", "memory": "256Mi"}
WORKLOAD_KINDS_WITH_TEMPLATE = {"Deployment", "StatefulSet", "DaemonSet", "Job", "ReplicaSet"}

_yaml = YAML()
_yaml.preserve_quotes = True
_yaml.indent(mapping=2, sequence=4, offset=2)


def _as_map(value: Any) -> CommentedMap | None:
    return value if isinstance(value, dict) else None


def _find_containers(doc: CommentedMap) -> list[Any]:
    kind = doc.get("kind")
    spec = _as_map(doc.get("spec")) or {}

    if kind == "Pod":
        containers = spec.get("containers")
    elif kind in WORKLOAD_KINDS_WITH_TEMPLATE:
        template = _as_map(spec.get("template")) or {}
        template_spec = _as_map(template.get("spec")) or {}
        containers = template_spec.get("containers")
    else:
        containers = None

    return containers if isinstance(containers, list) else []


def apply_fixes(content: str) -> tuple[str, list[str]]:
    """
    Returns (fixed_content, applied_fix_descriptions). If the content isn't
    valid YAML or isn't a mapping, returns it unchanged with no fixes applied
    — /fix never invents structure that isn't already there.
    """
def apply_fixes(content: str) -> tuple[str, list[str]]:
    """
    Returns (fixed_content, applied_fix_descriptions). If the content isn't
    valid YAML, returns it unchanged with no fixes applied — /fix never
    invents structure that isn't already there.

    Supports multi-document YAML (separated by '---'). Only the first
    document is patched, matching what /validate actually checks; later
    documents are carried through unchanged.
    """
    applied: list[str] = []

    try:
        docs = list(_yaml.load_all(content))
    except Exception:
        return content, applied

    if not docs or not isinstance(docs[0], dict):
        return content, applied

    doc = docs[0]

    kind = doc.get("kind")
    spec = _as_map(doc.get("spec"))

    # --- metadata.labels ---
    metadata = _as_map(doc.get("metadata"))
    if metadata is not None and not metadata.get("labels"):
        name = metadata.get("name")
        if name:
            metadata["labels"] = CommentedMap({"app": name})
            applied.append(f"Added metadata.labels: {{ app: {name} }}")

    if spec is not None:
        # --- replicas ---
        if kind in {"Deployment", "StatefulSet", "ReplicaSet"} and spec.get("replicas") is None:
            spec["replicas"] = 1
            applied.append("Added spec.replicas: 1")

        # --- selector.matchLabels, generated from template labels ---
        if kind == "Deployment":
            selector = _as_map(spec.get("selector"))
            match_labels = _as_map(selector.get("matchLabels")) if selector else None
            template = _as_map(spec.get("template"))
            template_metadata = _as_map(template.get("metadata")) if template else None
            template_labels = _as_map(template_metadata.get("labels")) if template_metadata else None

            if (not match_labels) and template_labels:
                new_selector = CommentedMap({"matchLabels": CommentedMap(template_labels)})
                spec["selector"] = new_selector
                applied.append("Generated spec.selector.matchLabels from template labels")

        # --- Service type default ---
        if kind == "Service" and not spec.get("type"):
            spec["type"] = "ClusterIP"
            applied.append("Added spec.type: ClusterIP (Kubernetes default)")

    # --- container resource defaults ---
    for container in _find_containers(doc):
        if not isinstance(container, dict):
            continue
        name = container.get("name", "unnamed")
        resources = _as_map(container.get("resources"))
        if resources is None:
            resources = CommentedMap()
            container["resources"] = resources

        if not resources.get("requests"):
            resources["requests"] = CommentedMap(DEFAULT_REQUESTS)
            applied.append(f"Added default resources.requests for container '{name}'")

        if not resources.get("limits"):
            resources["limits"] = CommentedMap(DEFAULT_LIMITS)
            applied.append(f"Added default resources.limits for container '{name}'")

    if not applied:
        return content, applied

    import io

    buffer = io.StringIO()
    _yaml.dump_all(docs, buffer)
    return buffer.getvalue(), applied
