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
