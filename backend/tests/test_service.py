"""Tests for service.py — Service-specific validation."""
from tests.conftest import dedent
from app.validators.service import check_service
from app.utils.yaml_parser import parse_yaml


def _doc(yaml_str: str):
    doc, _ = parse_yaml(yaml_str)
    return doc


VALID_SERVICE = dedent("""
    apiVersion: v1
    kind: Service
    metadata:
      name: my-svc
    spec:
      type: ClusterIP
      selector:
        app: my-app
      ports:
        - port: 80
          targetPort: 8080
""")


def test_valid_service_no_errors():
    doc = _doc(VALID_SERVICE)
    errors, warnings, passed = check_service(doc, VALID_SERVICE)
    assert errors == []
    # No type warning because type is set.
    type_warnings = [w for w in warnings if "type" in w.title.lower()]
    assert type_warnings == []


def test_missing_ports_is_error():
    content = dedent("""
        apiVersion: v1
        kind: Service
        metadata:
          name: my-svc
        spec:
          selector:
            app: my-app
    """)
    errors, warnings, _ = check_service(_doc(content), content)
    assert any("ports" in e.title.lower() for e in errors)


def test_port_entry_missing_port_number():
    content = dedent("""
        apiVersion: v1
        kind: Service
        metadata:
          name: my-svc
        spec:
          selector:
            app: my-app
          ports:
            - name: http
    """)
    errors, _, _ = check_service(_doc(content), content)
    assert any("missing 'port'" in e.title.lower() for e in errors)


def test_missing_selector_is_warning_not_error():
    content = dedent("""
        apiVersion: v1
        kind: Service
        metadata:
          name: my-svc
        spec:
          ports:
            - port: 80
    """)
    errors, warnings, _ = check_service(_doc(content), content)
    assert not any("selector" in e.title.lower() for e in errors)
    assert any("selector" in w.title.lower() for w in warnings)


def test_missing_type_is_warning():
    content = dedent("""
        apiVersion: v1
        kind: Service
        metadata:
          name: my-svc
        spec:
          selector:
            app: my-app
          ports:
            - port: 80
    """)
    _, warnings, _ = check_service(_doc(content), content)
    assert any("type" in w.title.lower() for w in warnings)


def test_invalid_type_is_error():
    content = dedent("""
        apiVersion: v1
        kind: Service
        metadata:
          name: my-svc
        spec:
          type: MadeUp
          selector:
            app: my-app
          ports:
            - port: 80
    """)
    errors, _, _ = check_service(_doc(content), content)
    assert any("Unrecognized service type" in e.title for e in errors)
