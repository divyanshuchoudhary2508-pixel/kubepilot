"""Tests for configmap_secret.py — ConfigMap and Secret validation."""
from tests.conftest import dedent
from app.validators.configmap_secret import check_configmap, check_secret
from app.utils.yaml_parser import parse_yaml


def _doc(yaml_str: str):
    doc, _ = parse_yaml(yaml_str)
    return doc


# ---------------------------------------------------------------------------
# ConfigMap
# ---------------------------------------------------------------------------

def test_configmap_with_data_passes():
    content = dedent("""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: my-config
        data:
          KEY: value
    """)
    warnings, passed = check_configmap(_doc(content), content)
    assert warnings == []
    assert any("data" in p.lower() for p in passed)


def test_configmap_empty_data_warns():
    content = dedent("""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: my-config
    """)
    warnings, _ = check_configmap(_doc(content), content)
    assert len(warnings) == 1
    assert warnings[0].severity == "low"


def test_configmap_with_binary_data_passes():
    content = dedent("""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: my-config
        binaryData:
          file.bin: dGVzdA==
    """)
    warnings, passed = check_configmap(_doc(content), content)
    assert warnings == []


# ---------------------------------------------------------------------------
# Secret
# ---------------------------------------------------------------------------

def test_secret_with_string_data_passes():
    content = dedent("""
        apiVersion: v1
        kind: Secret
        metadata:
          name: my-secret
        type: Opaque
        stringData:
          password: supersecret
    """)
    warnings, passed = check_secret(_doc(content), content)
    # Only the "data" check should be silent; type check should pass.
    data_warnings = [w for w in warnings if "no data" in w.title.lower()]
    assert data_warnings == []
    assert any("valid" in p.lower() for p in passed)


def test_secret_empty_warns():
    content = dedent("""
        apiVersion: v1
        kind: Secret
        metadata:
          name: my-secret
        type: Opaque
    """)
    warnings, _ = check_secret(_doc(content), content)
    assert any("no data" in w.title.lower() for w in warnings)


def test_secret_missing_type_warns():
    content = dedent("""
        apiVersion: v1
        kind: Secret
        metadata:
          name: my-secret
        stringData:
          key: val
    """)
    warnings, _ = check_secret(_doc(content), content)
    assert any("type" in w.title.lower() for w in warnings)


def test_secret_known_type_passes():
    content = dedent("""
        apiVersion: v1
        kind: Secret
        metadata:
          name: my-secret
        type: kubernetes.io/tls
        data:
          tls.crt: abc123
          tls.key: xyz789
    """)
    warnings, passed = check_secret(_doc(content), content)
    type_warnings = [w for w in warnings if "type" in w.title.lower()]
    assert type_warnings == []
