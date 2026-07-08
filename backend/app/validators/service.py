"""
Validation specific to kind: Service.

Checks: spec.selector, spec.ports (non-empty, each with a port number), and
spec.type (defaults to ClusterIP if omitted, so this is a warning, not an error).
"""

from __future__ import annotations

from app.schemas.manifest import Issue
from app.validators.line_finder import get_line

VALID_SERVICE_TYPES = {"ClusterIP", "NodePort", "LoadBalancer", "ExternalName"}


def check_service(doc: dict, content: str) -> tuple[list[Issue], list[Issue], list[str]]:
    """
    Returns (errors, warnings, passed_checks).
    """
    errors: list[Issue] = []
    warnings: list[Issue] = []
    passed: list[str] = []

    spec = doc.get("spec")
    if not isinstance(spec, dict):
        return errors, warnings, passed

    selector = spec.get("selector")
    if not isinstance(selector, dict) or not selector:
        warnings.append(
            Issue(
                line=get_line(content, ["spec"]),
                severity="medium",
                title="Missing selector",
                message="Service has no spec.selector. This is valid only for headless/ExternalName services "
                "that route via manually managed Endpoints.",
                suggestion="Add spec.selector matching the labels of the target Pods, unless this is intentional.",
            )
        )
    else:
        passed.append("spec.selector present")

    ports = spec.get("ports")
    if not isinstance(ports, list) or len(ports) == 0:
        errors.append(
            Issue(
                line=get_line(content, ["spec"]),
                severity="high",
                title="Missing ports",
                message="Service requires at least one entry in spec.ports.",
                suggestion="Add spec.ports with at least one { port: <number> } entry.",
            )
        )
    else:
        passed.append("spec.ports present")
        for index, port_entry in enumerate(ports):
            port_path = ["spec", "ports", index]
            if not isinstance(port_entry, dict) or port_entry.get("port") is None:
                errors.append(
                    Issue(
                        line=get_line(content, port_path),
                        severity="high",
                        title=f"Port entry #{index + 1} missing 'port'",
                        message="Each entry under spec.ports must specify a numeric 'port'.",
                        suggestion="Add 'port: <number>' to this entry.",
                    )
                )

    service_type = spec.get("type")
    if not service_type:
        warnings.append(
            Issue(
                line=get_line(content, ["spec"]),
                severity="low",
                title="Service type not specified",
                message="spec.type is not set; Kubernetes will default to ClusterIP.",
                suggestion="Add 'type: ClusterIP' explicitly if that's the intent, or set NodePort/LoadBalancer as needed.",
            )
        )
    elif service_type not in VALID_SERVICE_TYPES:
        errors.append(
            Issue(
                line=get_line(content, ["spec", "type"]),
                severity="medium",
                title="Unrecognized service type",
                message=f"'{service_type}' is not a standard Service type.",
                suggestion=f"Use one of: {', '.join(sorted(VALID_SERVICE_TYPES))}.",
            )
        )
    else:
        passed.append("spec.type valid")

    return errors, warnings, passed
