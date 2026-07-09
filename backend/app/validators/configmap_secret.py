"""
Validation specific to kind: ConfigMap and Secret.

ConfigMap checks:
  - Warn if data, binaryData are both absent/empty — an empty ConfigMap is valid
    but almost certainly not intentional.

Secret checks:
  - Same emptiness check across data, stringData, binaryData.
  - Warn if 'type' is not set (defaults to 'Opaque', explicit is clearer).
"""

from __future__ import annotations

from app.schemas.manifest import Issue
from app.validators.line_finder import get_line

COMMON_SECRET_TYPES = {
    "Opaque",
    "kubernetes.io/service-account-token",
    "kubernetes.io/dockercfg",
    "kubernetes.io/dockerconfigjson",
    "kubernetes.io/basic-auth",
    "kubernetes.io/ssh-auth",
    "kubernetes.io/tls",
    "bootstrap.kubernetes.io/token",
}


def check_configmap(
    doc: dict, content: str, doc_index: int = 0
) -> tuple[list[Issue], list[str]]:
    """
    Returns (warnings, passed_checks). ConfigMap has no hard-error checks —
    all issues here are best-practice warnings.
    """
    warnings: list[Issue] = []
    passed: list[str] = []

    def _warn(**kwargs) -> Issue:
        return Issue(**kwargs, document_index=doc_index if doc_index > 0 else None)

    data = doc.get("data")
    binary_data = doc.get("binaryData")

    data_empty = not isinstance(data, dict) or len(data) == 0
    binary_empty = not isinstance(binary_data, dict) or len(binary_data) == 0

    if data_empty and binary_empty:
        warnings.append(
            _warn(
                line=get_line(content, [], doc_index),
                severity="low",
                title="ConfigMap has no data",
                message="Both 'data' and 'binaryData' are absent or empty. "
                "This ConfigMap will be created but won't provide any configuration.",
                suggestion="Add a 'data:' block with key/value pairs, or 'binaryData:' for binary content.",
            )
        )
    else:
        passed.append("ConfigMap has data")

    return warnings, passed


def check_secret(
    doc: dict, content: str, doc_index: int = 0
) -> tuple[list[Issue], list[str]]:
    """
    Returns (warnings, passed_checks). Secrets have no hard-error checks here —
    all are best-practice warnings. (Presence of required fields is covered by
    check_required_fields.)
    """
    warnings: list[Issue] = []
    passed: list[str] = []

    def _warn(**kwargs) -> Issue:
        return Issue(**kwargs, document_index=doc_index if doc_index > 0 else None)

    data = doc.get("data")
    string_data = doc.get("stringData")
    binary_data = doc.get("binaryData")

    data_empty = not isinstance(data, dict) or len(data) == 0
    string_empty = not isinstance(string_data, dict) or len(string_data) == 0
    binary_empty = not isinstance(binary_data, dict) or len(binary_data) == 0

    if data_empty and string_empty and binary_empty:
        warnings.append(
            _warn(
                line=get_line(content, [], doc_index),
                severity="low",
                title="Secret has no data",
                message="'data', 'stringData', and 'binaryData' are all absent or empty. "
                "This Secret will be created but contains nothing.",
                suggestion="Add a 'stringData:' block (plain text, easier to read) or a 'data:' block (base64-encoded values).",
            )
        )
    else:
        passed.append("Secret has data")

    secret_type = doc.get("type")
    if not secret_type:
        warnings.append(
            _warn(
                line=get_line(content, [], doc_index),
                severity="low",
                title="Secret type not specified",
                message="'type' is not set; Kubernetes defaults to 'Opaque'. "
                "Being explicit makes the intent immediately clear to anyone reading the manifest.",
                suggestion="Add 'type: Opaque' (or the appropriate type, e.g. 'kubernetes.io/tls').",
            )
        )
    elif secret_type not in COMMON_SECRET_TYPES:
        # Not an error — custom types are valid. Just surface it so the user knows.
        warnings.append(
            _warn(
                line=get_line(content, ["type"], doc_index),
                severity="low",
                title="Non-standard Secret type",
                message=f"'{secret_type}' is not one of the built-in Kubernetes Secret types. "
                "This is fine if your controller expects it, but worth double-checking.",
                suggestion=f"Common types: {', '.join(sorted(COMMON_SECRET_TYPES))}.",
            )
        )
    else:
        passed.append("Secret type valid")

    return warnings, passed
