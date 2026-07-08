"""
Validation specific to kind: Deployment.

Checks: spec.selector.matchLabels, spec.template, spec.template.spec.containers,
and per-container name/image.
"""

from __future__ import annotations

from typing import Any

from app.schemas.manifest import Issue
from app.validators.line_finder import get_line


def _get_path(doc: dict, path: list[str]) -> Any:
    node = doc
    for segment in path:
        if not isinstance(node, dict):
            return None
        node = node.get(segment)
    return node


def check_deployment(doc: dict, content: str) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    passed: list[str] = []

    spec = doc.get("spec")
    if not isinstance(spec, dict):
        # Already reported by required_fields as "missing spec" — nothing more to check.
        return issues, passed

    match_labels = _get_path(doc, ["spec", "selector", "matchLabels"])
    if not isinstance(match_labels, dict) or not match_labels:
        issues.append(
            Issue(
                line=get_line(content, ["spec"]),
                severity="high",
                title="Missing selector",
                message="Deployment requires spec.selector.matchLabels.",
                suggestion="Add spec.selector.matchLabels matching the Pod template's labels.",
            )
        )
    else:
        passed.append("spec.selector.matchLabels present")

    template = spec.get("template")
    if not isinstance(template, dict):
        issues.append(
            Issue(
                line=get_line(content, ["spec"]),
                severity="high",
                title="Missing template",
                message="Deployment requires spec.template (the Pod template).",
                suggestion="Add a spec.template with metadata.labels and spec.containers.",
            )
        )
        return issues, passed
    else:
        passed.append("spec.template present")

    # Selector/template label match, when both exist.
    template_labels = _get_path(doc, ["spec", "template", "metadata", "labels"])
    if isinstance(match_labels, dict) and match_labels and isinstance(template_labels, dict):
        if not match_labels.items() <= template_labels.items():
            issues.append(
                Issue(
                    line=get_line(content, ["spec", "template", "metadata", "labels"]),
                    severity="high",
                    title="Selector does not match template labels",
                    message="spec.selector.matchLabels must be a subset of spec.template.metadata.labels.",
                    suggestion="Ensure every key/value in selector.matchLabels also appears in template.metadata.labels.",
                )
            )
        else:
            passed.append("selector matches template labels")

    containers = _get_path(doc, ["spec", "template", "spec", "containers"])
    if not isinstance(containers, list) or len(containers) == 0:
        issues.append(
            Issue(
                line=get_line(content, ["spec", "template", "spec"]),
                severity="high",
                title="Missing containers",
                message="Deployment requires at least one container under spec.template.spec.containers.",
                suggestion="Add a containers list with at least one container (name + image).",
            )
        )
    else:
        passed.append("spec.template.spec.containers present")
        for index, container in enumerate(containers):
            container_path = ["spec", "template", "spec", "containers", index]
            if not isinstance(container, dict):
                issues.append(
                    Issue(
                        line=get_line(content, container_path),
                        severity="high",
                        title=f"Container #{index + 1} is invalid",
                        message="Each entry under containers must be a mapping with at least 'name' and 'image'.",
                        suggestion="Define the container as a mapping, e.g. '- name: app\\n  image: my-image:1.0'.",
                    )
                )
                continue
            if not container.get("name"):
                issues.append(
                    Issue(
                        line=get_line(content, container_path),
                        severity="high",
                        title=f"Container #{index + 1} missing name",
                        message="Every container must have a 'name'.",
                        suggestion="Add a unique 'name:' field to the container.",
                    )
                )
            if not container.get("image"):
                issues.append(
                    Issue(
                        line=get_line(content, container_path),
                        severity="high",
                        title=f"Container '{container.get('name', index + 1)}' missing image",
                        message="Every container must have an 'image'.",
                        suggestion="Add an 'image:' field, e.g. 'image: nginx:1.27'.",
                    )
                )

    return issues, passed
