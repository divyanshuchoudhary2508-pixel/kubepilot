"""
Tests for engine.py — multi-document validation and end-to-end orchestration.

This test file specifically guards against the class of bug where multi-document
YAML is silently validated as if it were a single document (or silently ignored).
"""
from tests.conftest import dedent
from app.validators.engine import run_validation


def test_single_valid_deployment():
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
                  livenessProbe:
                    httpGet:
                      path: /healthz
                      port: 8080
                  readinessProbe:
                    httpGet:
                      path: /ready
                      port: 8080
    """)
    result = run_validation(content)
    assert result.valid
    assert result.score == 100
    assert result.document_count == 1


def test_invalid_yaml_returns_parse_error():
    content = "key: : broken"
    result = run_validation(content)
    assert not result.valid
    assert result.score == 0
    assert any("YAML syntax" in e.title for e in result.errors)
    assert result.document_count == 0


def test_empty_content_returns_error():
    result = run_validation("   \n  ")
    assert not result.valid
    assert result.document_count == 0


def test_multidoc_both_documents_validated():
    """
    THE key multi-doc regression test: errors from document 2 must appear
    in the result, proving doc 2 was actually validated.
    """
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: app-one
          labels:
            app: app-one
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: app-one
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
    """)
    result = run_validation(content)
    assert result.document_count == 2
    # Service is missing ports — that error must appear
    assert any("ports" in e.title.lower() for e in result.errors), (
        "Error from document 2 (Service missing ports) was not found — "
        "multi-document validation is silently skipping document 2."
    )


def test_multidoc_issues_tagged_with_document_index():
    """Issues from doc 2 must carry document_index=1."""
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: app-one
          labels:
            app: app-one
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: app-one
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
    """)
    result = run_validation(content)
    service_errors = [e for e in result.errors if "ports" in e.title.lower()]
    assert service_errors, "Service missing-ports error not found"
    assert service_errors[0].document_index == 1, (
        f"Expected document_index=1 for doc-2 error, got {service_errors[0].document_index}"
    )


def test_multidoc_score_aggregated_across_all_docs():
    """Score must reflect issues from all documents, not just the first."""
    # Doc 1 is fine. Doc 2 has a high-severity error.
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: app-one
          labels:
            app: app-one
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: app-one
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
    """)
    result = run_validation(content)
    assert result.score < 100, "Score should be reduced by errors from document 2"


def test_ingress_kind_validated():
    content = dedent("""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: my-ingress
        spec:
          ingressClassName: nginx
          rules: []
    """)
    result = run_validation(content)
    assert any("rules" in e.title.lower() for e in result.errors)


def test_configmap_kind_validated():
    content = dedent("""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: my-config
        spec: {}
    """)
    result = run_validation(content)
    # Should warn about empty data
    assert any("data" in w.title.lower() for w in result.warnings)


def test_secret_kind_validated():
    content = dedent("""
        apiVersion: v1
        kind: Secret
        metadata:
          name: my-secret
        spec: {}
    """)
    result = run_validation(content)
    assert any("data" in w.title.lower() for w in result.warnings)
