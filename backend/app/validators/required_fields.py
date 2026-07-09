"""
Checks that apply to every Kubernetes manifest regardless of kind:
apiVersion, kind, metadata (with a name), and spec must all be present.
"""

from __future__ import annotations

from typing import Any

from app.schemas.manifest import Issue
from app.validators.line_finder import get_line

REQUIRED_TOP_LEVEL_FIELDS = ["apiVersion", "kind", "metadata", "spec"]


def check_required_fields(
    doc: Any, content: str, doc_index: int = 0
) -> tuple[list[Issue], list[str]]:
    """
    Returns (issues, passed_checks) for the top-level required fields.
    """
    issues: list[Issue] = []
    passed: list[str] = []

    if not isinstance(doc, dict):
        issues.append(
            Issue(
                line=1,
                severity="high",
                title="Manifest is not a mapping",
                message="A Kubernetes manifest must be a YAML mapping (key/value document), not a list or scalar.",
                suggestion="Ensure the document starts with top-level keys like 'apiVersion:' and 'kind:'.",
                document_index=doc_index if doc_index > 0 else None,
            )
        )
        return issues, passed

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        value = doc.get(field)
        if value in (None, "", {}):
            issues.append(
                Issue(
                    line=get_line(content, [], doc_index),
                    severity="high",
                    title=f"Missing '{field}'",
                    message=f"Top-level '{field}' field is required on every Kubernetes manifest.",
                    suggestion=f"Add a top-level '{field}:' field.",
                    document_index=doc_index if doc_index > 0 else None,
                )
            )
        else:
            passed.append(f"Top-level '{field}' present")

    metadata = doc.get("metadata")
    if isinstance(metadata, dict):
        if not metadata.get("name"):
            issues.append(
                Issue(
                    line=get_line(content, ["metadata"], doc_index),
                    severity="high",
                    title="Missing metadata.name",
                    message="metadata.name is required to identify the resource.",
                    suggestion="Add 'name: <resource-name>' under metadata.",
                    document_index=doc_index if doc_index > 0 else None,
                )
            )
        else:
            passed.append("metadata.name present")

    return issues, passed
