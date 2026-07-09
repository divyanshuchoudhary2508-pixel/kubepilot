export const PLACEHOLDER_MANIFEST = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-app
spec:
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
        - name: app
          image: nginx:latest
`;

export interface ExampleManifest {
  label: string;
  description: string;
  content: string;
}

export const EXAMPLE_MANIFESTS: ExampleManifest[] = [
  {
    label: "Broken Deployment",
    description: "Missing selector, :latest image tag, no resource limits",
    content: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
        - name: web
          image: nginx:latest
`,
  },
  {
    label: "Broken Service",
    description: "Missing ports — the most common Service mistake",
    content: `apiVersion: v1
kind: Service
metadata:
  name: web-svc
spec:
  selector:
    app: web-app
`,
  },
  {
    label: "Broken Ingress",
    description: "Empty rules list, missing ingressClassName",
    content: `apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  rules: []
`,
  },
  {
    label: "Multi-doc: Deployment + Service",
    description: "Two documents in one file — both get validated",
    content: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
        - name: api
          image: my-api
---
apiVersion: v1
kind: Service
metadata:
  name: api-svc
spec:
  selector:
    app: api-server
`,
  },
  {
    label: "Empty ConfigMap",
    description: "Valid YAML, but the ConfigMap has no data",
    content: `apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
spec: {}
`,
  },
];
