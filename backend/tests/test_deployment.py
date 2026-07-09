"""Tests for deployment.py — Deployment-specific structural validation."""
from tests.conftest import dedent
from app.validators.deployment import check_deployment
from app.utils.yaml_parser import parse_yaml


def _doc(yaml_str: str):
    doc, _ = parse_yaml(yaml_str)
    return doc


VALID_DEPLOYMENT = dedent("""
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
""")


def test_valid_deployment_has_no_errors():
    doc = _doc(VALID_DEPLOYMENT)
    issues, passed = check_deployment(doc, VALID_DEPLOYMENT)
    assert issues == []
    assert "spec.selector.matchLabels present" in passed
    assert "spec.template present" in passed
    assert "spec.template.spec.containers present" in passed


def test_missing_selector():
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
    issues, _ = check_deployment(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("selector" in t.lower() for t in titles)


def test_selector_not_matching_template_labels():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          selector:
            matchLabels:
              app: other-name
          template:
            metadata:
              labels:
                app: my-app
            spec:
              containers:
                - name: app
                  image: nginx:1.27
    """)
    issues, _ = check_deployment(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("Selector does not match" in t for t in titles)


def test_missing_template():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec:
          selector:
            matchLabels:
              app: my-app
    """)
    issues, _ = check_deployment(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("template" in t.lower() for t in titles)


def test_missing_containers():
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
              containers: []
    """)
    issues, _ = check_deployment(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("containers" in t.lower() for t in titles)


def test_container_missing_name():
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
                - image: nginx:1.27
    """)
    issues, _ = check_deployment(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("missing name" in t.lower() for t in titles)


def test_container_missing_image():
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
    """)
    issues, _ = check_deployment(_doc(content), content)
    titles = [i.title for i in issues]
    assert any("missing image" in t.lower() for t in titles)


def test_all_errors_are_high_severity():
    content = dedent("""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-app
        spec: {}
    """)
    issues, _ = check_deployment(_doc(content), content)
    assert all(i.severity == "high" for i in issues)
