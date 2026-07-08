"""
Top-level orchestrator: parses YAML, runs the applicable rule modules based
on `kind`, and aggregates everything into a ValidationResponse.

Only the first YAML document is validated. Multi-document manifests
(separated by '---') are out of scope for this tool by design.
"""

from __future__ import annotations

from app.schemas.manifest import Issue, ValidationResponse
from app.utils.yaml_parser import parse_yaml
from app.validators.best_practices import check_best_practices
from app.validators.deployment import check_deployment
from app.validators.required_fields import check_required_fields
from app.validators.service import check_service

SEVERITY_PENALTY = {"high": 15, "medium": 8, "low": 3}


def _compute_score(errors: list[Issue], warnings: list[Issue]) -> int:
    score = 100
    for issue in errors + warnings:
        score -= SEVERITY_PENALTY.get(issue.severity, 5)
    return max(0, score)


def run_validation(content: str) -> ValidationResponse:
    doc, parse_error = parse_yaml(content)

    if parse_error is not None:
        error = Issue(
            line=parse_error.line,
            severity="high",
            title="Invalid YAML syntax",
            message=parse_error.message,
            suggestion="Check indentation and colon placement around the reported line.",
        )
        return ValidationResponse(valid=False, errors=[error], warnings=[], passed_checks=[], score=0)

    errors: list[Issue] = []
    warnings: list[Issue] = []
    passed: list[str] = []

    required_issues, required_passed = check_required_fields(doc, content)
    errors.extend(required_issues)
    passed.extend(required_passed)

    if isinstance(doc, dict):
        kind = doc.get("kind")

        if kind == "Deployment":
            deployment_issues, deployment_passed = check_deployment(doc, content)
            errors.extend(deployment_issues)
            passed.extend(deployment_passed)
        elif kind == "Service":
            service_errors, service_warnings, service_passed = check_service(doc, content)
            errors.extend(service_errors)
            warnings.extend(service_warnings)
            passed.extend(service_passed)

        # Best-practice checks run regardless of kind (they no-op gracefully
        # for kinds they don't understand).
        bp_warnings, bp_passed = check_best_practices(doc, content)
        warnings.extend(bp_warnings)
        passed.extend(bp_passed)

    score = _compute_score(errors, warnings)

    return ValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        passed_checks=passed,
        score=score,
    )
