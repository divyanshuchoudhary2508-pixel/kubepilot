"""Tests for fixers.py — deterministic manifest fixer."""
from tests.conftest import dedent
from app.validators.fixers import apply_fixes


def test_invalid_yaml_returned_unchanged():
    content = "this: is: broken: yaml: :::"
    result, fixes = apply_fixes(content)
    assert result == content
    assert fixes == []


def test_empty_input_returned_unchanged():
    result, fixes = apply_fixes("")
    assert result == ""
    assert fixes == []


def test_adds_replicas_when_missing():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          selector:
            matchLabels:
              app: my-app
          template:
            metadata:
              labels:
                app: my-app
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    fixed, fixes = apply_fixes(content)
    assert any("replicas" in f for f in fixes)
    assert "replicas: 1" in fixed


def test_adds_metadata_labels_from_name():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          replicas: 1
          template:
            metadata:
              labels:
                app: my-app
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    fixed, fixes = apply_fixes(content)
    assert any("metadata.labels" in f for f in fixes)
    assert "app: my-app" in fixed


def test_generates_selector_from_template_labels():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          template:
            metadata:
              labels:
                app: my-app
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    fixed, fixes = apply_fixes(content)
    assert any("selector" in f.lower() for f in fixes)
    assert "matchLabels" in fixed


def test_adds_default_service_type():
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
    fixed, fixes = apply_fixes(content)
    assert any("ClusterIP" in f for f in fixes)
    assert "ClusterIP" in fixed


def test_adds_resource_requests_and_limits():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: my-app
          template:
            metadata:
              labels:
                app: my-app
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    fixed, fixes = apply_fixes(content)
    assert any("requests" in f for f in fixes)
    assert any("limits" in f for f in fixes)
    assert "cpu: 100m" in fixed
    assert "memory: 128Mi" in fixed


def test_no_fixes_returns_original_content():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: my-app
          template:
            metadata:
              labels:
                app: my-app
            spec:
              containers:
                - name: app
                  image: nginx:1.27
                  resources:
                    requests:
                      cpu: 100m
                      memory: 128Mi
                    limits:
                      cpu: 500m
                      memory: 256Mi
    """)
    _, fixes = apply_fixes(content)
    assert fixes == []


def test_multidoc_both_docs_fixed():
    """
    Regression test for the class of bug where multi-document YAML was
    returned unchanged or only the first doc was patched.
    """
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: app-one
        spec:
          template:
            metadata:
              labels:
                app: app-one
            spec:
              containers:
                - name: app
                  image: nginx:1.27
        ---
        apiVersion: v1
        kind: Service
        metadata:
          name: svc-one
        spec:
          selector:
            app: app-one
          ports:
            - port: 80
    """)
    fixed, fixes = apply_fixes(content)
    # Both docs should be present in output
    assert "app-one" in fixed
    assert "svc-one" in fixed
    # Fixes from both documents
    assert any("replicas" in f for f in fixes)
    assert any("ClusterIP" in f for f in fixes)
    # Output must contain both document separators
    assert "---" in fixed
