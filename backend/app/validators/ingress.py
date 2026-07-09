"""
Validation specific to kind: Ingress.

Checks:
  - spec.rules is a non-empty list
  - Each rule has http.paths as a non-empty list
  - Each path has 'path', 'pathType', and backend.service with name + port
  - Warns if spec.ingressClassName is missing (valid to rely on default, but explicit is better)
"""

from __future__ import annotations

from app.schemas.manifest import Issue
from app.validators.line_finder import get_line


def check_ingress(
    doc: dict, content: str, doc_index: int = 0
) -> tuple[list[Issue], list[Issue], list[str]]:
    """
    Returns (errors, warnings, passed_checks).
    """
    errors: list[Issue] = []
    warnings: list[Issue] = []
    passed: list[str] = []

    def _err(**kwargs) -> Issue:
        return Issue(**kwargs, document_index=doc_index if doc_index > 0 else None)

    spec = doc.get("spec")
    if not isinstance(spec, dict):
        return errors, warnings, passed

    # --- ingressClassName (warn, not error — default IngressClass is valid) ---
    if not spec.get("ingressClassName"):
        warnings.append(
            _err(
                line=get_line(content, ["spec"], doc_index),
                severity="low",
                title="Missing ingressClassName",
                message="spec.ingressClassName is not set. Kubernetes will use the cluster's default IngressClass if one exists, "
                "which may not be what you intended.",
                suggestion="Add 'ingressClassName: nginx' (or whichever controller you're using) to be explicit.",
            )
        )
    else:
        passed.append("spec.ingressClassName present")

    # --- rules ---
    rules = spec.get("rules")
    if not isinstance(rules, list) or len(rules) == 0:
        errors.append(
            _err(
                line=get_line(content, ["spec"], doc_index),
                severity="high",
                title="Missing spec.rules",
                message="An Ingress with no rules will never route any traffic.",
                suggestion="Add at least one entry under spec.rules with an http.paths configuration.",
            )
        )
        return errors, warnings, passed

    passed.append("spec.rules present")

    for rule_idx, rule in enumerate(rules):
        rule_path = ["spec", "rules", rule_idx]
        if not isinstance(rule, dict):
            errors.append(
                _err(
                    line=get_line(content, rule_path, doc_index),
                    severity="high",
                    title=f"Rule #{rule_idx + 1} is not a mapping",
                    message="Each entry in spec.rules must be a YAML mapping.",
                    suggestion="Define the rule as a mapping with optional 'host' and required 'http.paths'.",
                )
            )
            continue

        http = rule.get("http")
        if not isinstance(http, dict):
            errors.append(
                _err(
                    line=get_line(content, rule_path, doc_index),
                    severity="high",
                    title=f"Rule #{rule_idx + 1} missing http",
                    message="Each Ingress rule must have an 'http' block with a 'paths' list.",
                    suggestion="Add 'http:\\n  paths:' under this rule.",
                )
            )
            continue

        paths = http.get("paths")
        if not isinstance(paths, list) or len(paths) == 0:
            errors.append(
                _err(
                    line=get_line(content, rule_path + ["http"], doc_index),
                    severity="high",
                    title=f"Rule #{rule_idx + 1} has empty http.paths",
                    message="http.paths must have at least one entry for the rule to route traffic.",
                    suggestion="Add at least one path entry with path, pathType, and backend.service.",
                )
            )
            continue

        for path_idx, path_entry in enumerate(paths):
            path_loc = rule_path + ["http", "paths", path_idx]
            if not isinstance(path_entry, dict):
                errors.append(
                    _err(
                        line=get_line(content, path_loc, doc_index),
                        severity="high",
                        title=f"Rule #{rule_idx + 1}, path #{path_idx + 1} is not a mapping",
                        message="Each path entry must be a mapping with path, pathType, and backend.",
                        suggestion="Define path as a mapping, e.g. '- path: / pathType: Prefix backend: ...'.",
                    )
                )
                continue

            if not path_entry.get("path"):
                errors.append(
                    _err(
                        line=get_line(content, path_loc, doc_index),
                        severity="high",
                        title=f"Rule #{rule_idx + 1}, path #{path_idx + 1} missing 'path'",
                        message="Each path entry must have a 'path' field (e.g. '/' or '/api').",
                        suggestion="Add 'path: /' or the specific URL path prefix this rule should match.",
                    )
                )

            if not path_entry.get("pathType"):
                errors.append(
                    _err(
                        line=get_line(content, path_loc, doc_index),
                        severity="high",
                        title=f"Rule #{rule_idx + 1}, path #{path_idx + 1} missing 'pathType'",
                        message="'pathType' is required. It controls how the path is matched.",
                        suggestion="Add 'pathType: Prefix' (or 'Exact' or 'ImplementationSpecific').",
                    )
                )

            backend = path_entry.get("backend") if isinstance(path_entry.get("backend"), dict) else {}
            service = backend.get("service") if isinstance(backend.get("service"), dict) else {}

            if not service:
                errors.append(
                    _err(
                        line=get_line(content, path_loc, doc_index),
                        severity="high",
                        title=f"Rule #{rule_idx + 1}, path #{path_idx + 1} missing backend.service",
                        message="Each path entry must point to a Service via backend.service.",
                        suggestion="Add 'backend:\\n  service:\\n    name: my-svc\\n    port:\\n      number: 80'.",
                    )
                )
            else:
                if not service.get("name"):
                    errors.append(
                        _err(
                            line=get_line(content, path_loc + ["backend", "service"], doc_index),
                            severity="high",
                            title=f"Rule #{rule_idx + 1}, path #{path_idx + 1} backend.service missing name",
                            message="backend.service.name must identify which Service to route to.",
                            suggestion="Add 'name: <your-service-name>' under backend.service.",
                        )
                    )
                port = service.get("port")
                if not isinstance(port, dict) or (
                    port.get("number") is None and not port.get("name")
                ):
                    errors.append(
                        _err(
                            line=get_line(content, path_loc + ["backend", "service"], doc_index),
                            severity="high",
                            title=f"Rule #{rule_idx + 1}, path #{path_idx + 1} backend.service missing port",
                            message="backend.service.port must specify either a numeric 'number' or a named 'name'.",
                            suggestion="Add 'port:\\n  number: 80' under backend.service.",
                        )
                    )

    return errors, warnings, passed
