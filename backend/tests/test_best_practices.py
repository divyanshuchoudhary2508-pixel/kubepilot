"""Tests for best_practices.py — cross-kind best-practice warnings."""
from tests.conftest import dedent
from app.validators.best_practices import check_best_practices
from app.utils.yaml_parser import parse_yaml


def _doc(yaml_str: str):
    doc, _ = parse_yaml(yaml_str)
    return doc


def test_fully_specified_deployment_passes_all():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          replicas: 3
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
    warnings, passed = check_best_practices(_doc(content), content)
    assert warnings == []
    assert "metadata.labels present" in passed
    assert "spec.replicas present" in passed


def test_latest_tag_warns():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          replicas: 1
          template:
            spec:
              containers:
                - name: app
                  image: nginx:latest
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    assert any("floating tag" in w.title.lower() for w in warnings)


def test_no_tag_warns():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          replicas: 1
          template:
            spec:
              containers:
                - name: app
                  image: nginx
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    assert any("floating tag" in w.title.lower() for w in warnings)


def test_missing_resource_requests_warns():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          replicas: 1
          template:
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    assert any("resource requests" in w.title.lower() for w in warnings)
    assert any("resource limits" in w.title.lower() for w in warnings)


def test_missing_probes_warn():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          replicas: 1
          template:
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    assert any("livenessProbe" in w.title for w in warnings)
    assert any("readinessProbe" in w.title for w in warnings)


def test_missing_replicas_warns():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
          labels:
            app: my-app
        spec:
          template:
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    assert any("replicas" in w.title.lower() for w in warnings)


def test_missing_labels_warns():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          replicas: 1
          template:
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    assert any("labels" in w.title.lower() for w in warnings)


def test_pod_kind_uses_spec_containers():
    content = dedent("""
        apiVersion: v1
        kind: Pod
        metadata:
          name: my-pod
          labels:
            app: my-pod
        spec:
          containers:
            - name: app
              image: nginx:latest
    """)
    warnings, _ = check_best_practices(_doc(content), content)
    # Should flag the :latest tag even though kind is Pod
    assert any("floating tag" in w.title.lower() for w in warnings)
