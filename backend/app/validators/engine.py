"""
Top-level orchestrator: parses YAML (including multi-document streams),
runs the applicable rule modules based on `kind` for each document, and
aggregates everything into a ValidationResponse.

Multi-document YAML (separated by '---') is fully supported: every document
is validated independently, and each Issue is tagged with its document_index
so the frontend can display "Doc 1 / Doc 2" labels and route Monaco markers
to the correct lines.
"""

from __future__ import annotations

from app.schemas.manifest import Issue, ValidationResponse
from app.utils.yaml_parser import parse_all_yaml
from app.validators.best_practices import check_best_practices
from app.validators.configmap_secret import check_configmap, check_secret
from app.validators.deployment import check_deployment
from app.validators.ingress import check_ingress
from app.validators.required_fields import check_required_fields
from app.validators.service import check_service

SEVERITY_PENALTY = {"high": 15, "medium": 8, "low": 3}


def _compute_score(errors: list[Issue], warnings: list[Issue]) -> int:
    score = 100
    for issue in errors + warnings:
        score -= SEVERITY_PENALTY.get(issue.severity, 5)
    return max(0, score)


def _validate_single_doc(
    doc: object, content: str, doc_index: int
) -> tuple[list[Issue], list[Issue], list[str]]:
    """
    Run all validators against one parsed document.
    Returns (errors, warnings, passed_checks).
    """
    errors: list[Issue] = []
    warnings: list[Issue] = []
    passed: list[str] = []

    required_issues, required_passed = check_required_fields(doc, content, doc_index)
    errors.extend(required_issues)
    passed.extend(required_passed)

    if not isinstance(doc, dict):
        return errors, warnings, passed

    kind = doc.get("kind")

    if kind == "Deployment":
        deployment_issues, deployment_passed = check_deployment(doc, content, doc_index)
        errors.extend(deployment_issues)
        passed.extend(deployment_passed)

    elif kind == "Service":
        svc_errors, svc_warnings, svc_passed = check_service(doc, content, doc_index)
        errors.extend(svc_errors)
        warnings.extend(svc_warnings)
        passed.extend(svc_passed)

    elif kind == "Ingress":
        ing_errors, ing_warnings, ing_passed = check_ingress(doc, content, doc_index)
        errors.extend(ing_errors)
        warnings.extend(ing_warnings)
        passed.extend(ing_passed)

    elif kind == "ConfigMap":
        cm_warnings, cm_passed = check_configmap(doc, content, doc_index)
        warnings.extend(cm_warnings)
        passed.extend(cm_passed)

    elif kind == "Secret":
        sec_warnings, sec_passed = check_secret(doc, content, doc_index)
        warnings.extend(sec_warnings)
        passed.extend(sec_passed)

    # Best-practice checks run for all workload kinds (no-op gracefully for others).
    bp_warnings, bp_passed = check_best_practices(doc, content, doc_index)
    warnings.extend(bp_warnings)
    passed.extend(bp_passed)

    return errors, warnings, passed


def run_validation(content: str) -> ValidationResponse:
    docs, parse_error = parse_all_yaml(content)

    if parse_error is not None:
        error = Issue(
            line=parse_error.line,
            severity="high",
            title="Invalid YAML syntax",
            message=parse_error.message,
            suggestion="Check indentation and colon placement around the reported line.",
        )
        return ValidationResponse(
            valid=False,
            errors=[error],
            warnings=[],
            passed_checks=[],
            score=0,
            document_count=0,
        )

    if not docs:
        error = Issue(
            line=1,
            severity="high",
            title="Empty manifest",
            message="The submitted content contains no YAML documents.",
            suggestion="Paste or upload a Kubernetes manifest.",
        )
        return ValidationResponse(
            valid=False,
            errors=[error],
            warnings=[],
            passed_checks=[],
            score=0,
            document_count=0,
        )

    all_errors: list[Issue] = []
    all_warnings: list[Issue] = []
    all_passed: list[str] = []

    for doc_index, doc in enumerate(docs):
        errors, warnings, passed = _validate_single_doc(doc, content, doc_index)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        all_passed.extend(passed)

    score = _compute_score(all_errors, all_warnings)

    return ValidationResponse(
        valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        passed_checks=all_passed,
        score=score,
        document_count=len(docs),
    )
