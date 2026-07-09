"""
Best-practice checks. These never block validity (they only ever produce
warnings, not errors) — they're recommendations, not spec requirements.

Applies to any kind that has a Pod-shaped container list: Deployment,
StatefulSet, DaemonSet, Job, ReplicaSet (via spec.template.spec.containers)
or a bare Pod (via spec.containers).
"""

from __future__ import annotations

from typing import Any

from app.schemas.manifest import Issue
from app.validators.line_finder import get_line

WORKLOAD_KINDS_WITH_TEMPLATE = {"Deployment", "StatefulSet", "DaemonSet", "Job", "ReplicaSet"}


def _find_containers(doc: dict) -> tuple[list[Any], list[str]]:
    """Returns (containers, path_to_containers) for whichever shape applies."""
    kind = doc.get("kind")
    spec = doc.get("spec") if isinstance(doc.get("spec"), dict) else {}

    if kind == "Pod":
        containers = spec.get("containers")
        path = ["spec", "containers"]
    elif kind in WORKLOAD_KINDS_WITH_TEMPLATE:
        template = spec.get("template") if isinstance(spec.get("template"), dict) else {}
        template_spec = template.get("spec") if isinstance(template.get("spec"), dict) else {}
        containers = template_spec.get("containers")
        path = ["spec", "template", "spec", "containers"]
    else:
        containers, path = None, []

    return (containers if isinstance(containers, list) else []), path


def check_best_practices(
    doc: dict, content: str, doc_index: int = 0
) -> tuple[list[Issue], list[str]]:
    warnings: list[Issue] = []
    passed: list[str] = []

    def _issue(**kwargs) -> Issue:
        return Issue(**kwargs, document_index=doc_index if doc_index > 0 else None)

    kind = doc.get("kind")
    spec = doc.get("spec") if isinstance(doc.get("spec"), dict) else {}

    # --- labels on the resource itself ---
    metadata = doc.get("metadata") if isinstance(doc.get("metadata"), dict) else {}
    if not metadata.get("labels"):
        warnings.append(
            _issue(
                line=get_line(content, ["metadata"], doc_index),
                severity="low",
                title="Missing labels",
                message="metadata.labels is empty or missing. Labels make resources easier to select, filter, and organize.",
                suggestion="Add metadata.labels, e.g. { app: my-app }.",
            )
        )
    else:
        passed.append("metadata.labels present")

    # --- replicas (Deployment/StatefulSet/ReplicaSet only) ---
    if kind in {"Deployment", "StatefulSet", "ReplicaSet"}:
        if spec.get("replicas") is None:
            warnings.append(
                _issue(
                    line=get_line(content, ["spec"], doc_index),
                    severity="low",
                    title="Missing replicas",
                    message="spec.replicas is not set; Kubernetes defaults to 1, but being explicit avoids surprises.",
                    suggestion="Add 'replicas: 1' (or your desired count) under spec.",
                )
            )
        else:
            passed.append("spec.replicas present")

    containers, containers_path = _find_containers(doc)
    if not containers:
        return warnings, passed

    for index, container in enumerate(containers):
        if not isinstance(container, dict):
            continue

        name = container.get("name", f"#{index + 1}")
        container_path = containers_path + [index]

        image = container.get("image")
        if isinstance(image, str):
            if image.endswith(":latest") or ":" not in image:
                warnings.append(
                    _issue(
                        line=get_line(content, container_path + ["image"], doc_index),
                        severity="medium",
                        title=f"Container '{name}' uses a floating tag",
                        message="Using ':latest' (or no tag at all) makes deployments non-reproducible.",
                        suggestion="Pin the image to a specific version, e.g. 'nginx:1.27.0'.",
                    )
                )

        resources = container.get("resources") if isinstance(container.get("resources"), dict) else {}
        if not resources.get("requests"):
            warnings.append(
                _issue(
                    line=get_line(content, container_path, doc_index),
                    severity="medium",
                    title=f"Container '{name}' missing resource requests",
                    message="No resources.requests set. The scheduler can't make good placement decisions without it.",
                    suggestion="Add resources.requests, e.g. { cpu: '100m', memory: '128Mi' }.",
                )
            )
        if not resources.get("limits"):
            warnings.append(
                _issue(
                    line=get_line(content, container_path, doc_index),
                    severity="medium",
                    title=f"Container '{name}' missing resource limits",
                    message="No resources.limits set. A single container could consume unbounded node resources.",
                    suggestion="Add resources.limits, e.g. { cpu: '500m', memory: '256Mi' }.",
                )
            )

        if not container.get("livenessProbe"):
            warnings.append(
                _issue(
                    line=get_line(content, container_path, doc_index),
                    severity="low",
                    title=f"Container '{name}' missing livenessProbe",
                    message="Without a livenessProbe, Kubernetes can't detect and restart a hung container.",
                    suggestion="Add a livenessProbe (httpGet, tcpSocket, or exec).",
                )
            )
        if not container.get("readinessProbe"):
            warnings.append(
                _issue(
                    line=get_line(content, container_path, doc_index),
                    severity="low",
                    title=f"Container '{name}' missing readinessProbe",
                    message="Without a readinessProbe, traffic may be routed to a container before it's ready.",
                    suggestion="Add a readinessProbe (httpGet, tcpSocket, or exec).",
                )
            )

    return warnings, passed
