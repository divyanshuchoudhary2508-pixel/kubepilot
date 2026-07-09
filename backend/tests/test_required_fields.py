"""Tests for required_fields.py — the checks that apply to every manifest."""
import pytest
from tests.conftest import dedent
from app.validators.required_fields import check_required_fields
from app.utils.yaml_parser import parse_yaml


def _doc(yaml_str: str):
    doc, _ = parse_yaml(yaml_str)
    return doc


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_valid_minimal_manifest_passes():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          replicas: 1
    """)
    issues, passed = check_required_fields(_doc(content), content)
    assert issues == []
    assert any("apiVersion" in p for p in passed)
    assert any("kind" in p for p in passed)
    assert any("metadata.name" in p for p in passed)


# ---------------------------------------------------------------------------
# Failure tests — each missing field gets its own test
# ---------------------------------------------------------------------------

def test_missing_api_version():
    content = dedent("""
        kind: Deployment
        metadata:
          name: my-app
        spec: {}
    """)
    issues, _ = check_required_fields(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("apiVersion" in t for t in titles)


def test_missing_kind():
    content = dedent("""
        apiVersion: apps/v1
        metadata:
          name: my-app
        spec: {}
    """)
    issues, _ = check_required_fields(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("kind" in t for t in titles)


def test_missing_metadata():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        spec: {}
    """)
    issues, _ = check_required_fields(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("metadata" in t for t in titles)


def test_missing_metadata_name():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          labels:
            app: foo
        spec: {}
    """)
    issues, _ = check_required_fields(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("metadata.name" in t for t in titles)


def test_missing_spec():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
    """)
    issues, _ = check_required_fields(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("spec" in t for t in titles)


def test_non_mapping_document():
    content = "- item1\n- item2\n"
    doc, _ = parse_yaml(content)
    issues, _ = check_required_fields(doc, content)
    assert any("not a mapping" in i.title.lower() for i in issues)
    assert all(i.severity == "high" for i in issues)


def test_all_issues_have_severity_high():
    content = dedent("""
        metadata:
          name: foo
    """)
    issues, _ = check_required_fields(_doc(content), content)
    assert all(i.severity == "high" for i in issues)
