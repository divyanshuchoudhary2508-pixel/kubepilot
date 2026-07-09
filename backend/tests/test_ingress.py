"""Tests for ingress.py — Ingress-specific validation."""
from tests.conftest import dedent
from app.validators.ingress import check_ingress
from app.utils.yaml_parser import parse_yaml


def _doc(yaml_str: str):
    doc, _ = parse_yaml(yaml_str)
    return doc


VALID_INGRESS = dedent("""
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: my-ingress
    spec:
      ingressClassName: nginx
      rules:
        - host: example.com
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: my-svc
                    port:
                      number: 80
""")


def test_valid_ingress_no_errors():
    doc = _doc(VALID_INGRESS)
    errors, warnings, passed = check_ingress(doc, VALID_INGRESS)
    assert errors == []
    # No ingressClassName warning
    assert not any("ingressClassName" in w.title for w in warnings)


def test_missing_rules_is_error():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          ingressClassName: nginx
    """)
    errors, _, _ = check_ingress(_doc(content), content)
    assert any("rules" in e.title.lower() for e in errors)


def test_empty_rules_is_error():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          rules: []
    """)
    errors, _, _ = check_ingress(_doc(content), content)
    assert any("rules" in e.title.lower() for e in errors)


def test_missing_http_paths_is_error():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          rules:
            - host: example.com
              http:
                paths: []
    """)
    errors, _, _ = check_ingress(_doc(content), content)
    assert any("paths" in e.title.lower() for e in errors)


def test_missing_path_field_is_error():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          rules:
            - host: example.com
              http:
                paths:
                  - pathType: Prefix
                    backend:
                      service:
                        name: my-svc
                        port:
                          number: 80
    """)
    errors, _, _ = check_ingress(_doc(content), content)
    assert any("missing 'path'" in e.title.lower() for e in errors)


def test_missing_path_type_is_error():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          rules:
            - host: example.com
              http:
                paths:
                  - path: /
                    backend:
                      service:
                        name: my-svc
                        port:
                          number: 80
    """)
    errors, _, _ = check_ingress(_doc(content), content)
    assert any("pathtype" in e.title.lower() for e in errors)


def test_missing_backend_service_is_error():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          rules:
            - host: example.com
              http:
                paths:
                  - path: /
                    pathType: Prefix
    """)
    errors, _, _ = check_ingress(_doc(content), content)
    assert any("backend.service" in e.title.lower() for e in errors)


def test_missing_ingress_class_name_is_warning():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          rules:
            - host: example.com
              http:
                paths:
                  - path: /
                    pathType: Prefix
                    backend:
                      service:
                        name: my-svc
                        port:
                          number: 80
    """)
    errors, warnings, _ = check_ingress(_doc(content), content)
    assert not any("ingressClassName" in e.title for e in errors)
    assert any("ingressClassName" in w.title for w in warnings)
