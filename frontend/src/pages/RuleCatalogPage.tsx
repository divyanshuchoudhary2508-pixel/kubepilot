import { AlertTriangle, CheckCircle2, Info } from "lucide-react";

interface Rule {
  name: string;
  why: string;
  severity: "high" | "medium" | "low" | "info";
  kinds?: string[];
}

interface Category {
  title: string;
  description: string;
  rules: Rule[];
}

const CATALOG: Category[] = [
  {
    title: "Required Fields",
    description:
      "Every Kubernetes manifest must have these fields — without them, kubectl will reject the object outright.",
    rules: [
      {
        name: "apiVersion must be present",
        why: "Kubernetes uses apiVersion to route the request to the correct API handler. Without it, the API server doesn't know what kind of object you're creating.",
        severity: "high",
      },
      {
        name: "kind must be present",
        why: "kind tells Kubernetes what type of object this is (Deployment, Service, etc.). It's the most fundamental field.",
        severity: "high",
      },
      {
        name: "metadata must be present",
        why: "metadata holds the object's name, namespace, and labels. Without it the API server can't store or identify the object.",
        severity: "high",
      },
      {
        name: "metadata.name must be present",
        why: "Every Kubernetes object needs a name so it can be referenced, updated, or deleted. A nameless object can't be managed.",
        severity: "high",
      },
      {
        name: "spec must be present",
        why: "spec is where the actual desired state lives. Without it, the object has no configuration — it's like a box with no contents.",
        severity: "high",
      },
    ],
  },
  {
    title: "Deployment",
    description:
      "Deep structural checks specific to Deployments — the most common workload type.",
    rules: [
      {
        name: "spec.selector.matchLabels must be present",
        why: "The selector tells the Deployment which Pods it manages. Without it Kubernetes has no way to track which Pods belong to this Deployment.",
        severity: "high",
        kinds: ["Deployment"],
      },
      {
        name: "Selector must match template labels",
        why: "If the selector and the Pod template labels don't agree, the Deployment will create Pods it can never find — leading to runaway Pod creation or a stuck rollout.",
        severity: "high",
        kinds: ["Deployment"],
      },
      {
        name: "spec.template must be present",
        why: "The template is the blueprint for the Pods a Deployment creates. No template means no Pods.",
        severity: "high",
        kinds: ["Deployment"],
      },
      {
        name: "At least one container must be defined",
        why: "A Pod with no containers does nothing. Kubernetes requires at least one.",
        severity: "high",
        kinds: ["Deployment"],
      },
      {
        name: "Each container must have a name",
        why: "Container names are used in logs, exec commands, and multi-container Pods. Without a name, Kubernetes rejects the manifest.",
        severity: "high",
        kinds: ["Deployment", "Pod", "StatefulSet", "DaemonSet"],
      },
      {
        name: "Each container must have an image",
        why: "Without an image, Kubernetes doesn't know what to run. The container will fail to start and the Pod will go into an error loop.",
        severity: "high",
        kinds: ["Deployment", "Pod", "StatefulSet", "DaemonSet"],
      },
    ],
  },
  {
    title: "Service",
    description: "Checks specific to Services — the networking glue between workloads.",
    rules: [
      {
        name: "spec.ports must have at least one entry",
        why: "A Service with no ports is effectively a no-op. Without ports, no traffic can be routed.",
        severity: "high",
        kinds: ["Service"],
      },
      {
        name: "Each port entry must have a 'port' number",
        why: "The port field is what clients connect to. Without it, the port entry is incomplete and Kubernetes will reject it.",
        severity: "high",
        kinds: ["Service"],
      },
      {
        name: "spec.selector should be present",
        why: "Without a selector, the Service won't automatically route to any Pods. This is valid for headless Services and ExternalName, but usually a mistake for regular Services.",
        severity: "medium",
        kinds: ["Service"],
      },
      {
        name: "spec.type should be specified",
        why: "Kubernetes defaults to ClusterIP when type is omitted. Being explicit makes the intent clear when reading the manifest months later.",
        severity: "low",
        kinds: ["Service"],
      },
    ],
  },
  {
    title: "Ingress",
    description: "Checks specific to Ingress resources — the HTTP routing layer.",
    rules: [
      {
        name: "spec.rules must be non-empty",
        why: "An Ingress with no rules doesn't route any traffic. It's almost always an incomplete manifest.",
        severity: "high",
        kinds: ["Ingress"],
      },
      {
        name: "Each rule must have http.paths",
        why: "The paths list is what maps URL paths to backend Services. An empty paths list means the rule matches but sends traffic nowhere.",
        severity: "high",
        kinds: ["Ingress"],
      },
      {
        name: "Each path must have 'path' and 'pathType'",
        why: "Both are required by the Kubernetes API. Missing either will cause the manifest to be rejected. pathType (Prefix/Exact) controls how URLs are matched.",
        severity: "high",
        kinds: ["Ingress"],
      },
      {
        name: "Each path must have a backend.service with name and port",
        why: "This is the actual pointer to the Service that handles traffic for this path. Without it, routing has no destination.",
        severity: "high",
        kinds: ["Ingress"],
      },
      {
        name: "spec.ingressClassName should be specified",
        why: "Without ingressClassName, Kubernetes uses the cluster's default IngressClass — which might not be what you intend, and differs between clusters. Explicit is always safer.",
        severity: "low",
        kinds: ["Ingress"],
      },
    ],
  },
  {
    title: "ConfigMap & Secret",
    description: "Checks for configuration and secret resources.",
    rules: [
      {
        name: "ConfigMap should have data or binaryData",
        why: "An empty ConfigMap will be created but provides no configuration. This is almost always a forgotten step rather than an intentional choice.",
        severity: "low",
        kinds: ["ConfigMap"],
      },
      {
        name: "Secret should have data, stringData, or binaryData",
        why: "An empty Secret stores nothing. Like an empty ConfigMap, this is usually left over from scaffolding.",
        severity: "low",
        kinds: ["Secret"],
      },
      {
        name: "Secret type should be specified",
        why: "Kubernetes defaults to Opaque, but being explicit — especially for TLS or Docker credentials — makes the manifest self-documenting.",
        severity: "low",
        kinds: ["Secret"],
      },
    ],
  },
  {
    title: "Best Practices",
    description:
      "These checks don't block validity but help prevent common operational problems in production.",
    rules: [
      {
        name: "metadata.labels should be present",
        why: "Labels are how you select, filter, and group resources. Without them, kubectl get, selectors, and monitoring queries all become harder. Add at minimum { app: <name> }.",
        severity: "low",
      },
      {
        name: "spec.replicas should be explicit",
        why: "Kubernetes defaults to 1 replica when the field is absent. Being explicit prevents surprises when someone runs kubectl apply and wonders why there's only one Pod.",
        severity: "low",
        kinds: ["Deployment", "StatefulSet", "ReplicaSet"],
      },
      {
        name: "Don't use :latest or untagged images",
        why: "':latest' means 'whatever is newest right now', which changes without warning. Two nodes in the same cluster might pull different versions. Always pin to a specific digest or version tag.",
        severity: "medium",
      },
      {
        name: "Set resource requests",
        why: "The Kubernetes scheduler uses requests to decide which node to place a Pod on. Without requests, the scheduler guesses, and Pods may land on overloaded nodes.",
        severity: "medium",
      },
      {
        name: "Set resource limits",
        why: "Without limits, a single container can consume all CPU or memory on a node, starving other workloads. Limits are your safety net against runaway processes.",
        severity: "medium",
      },
      {
        name: "Set a livenessProbe",
        why: "Kubernetes uses the liveness probe to detect stuck containers and restart them. Without it, a container that locks up will just sit there consuming resources until someone notices.",
        severity: "low",
      },
      {
        name: "Set a readinessProbe",
        why: "Kubernetes only routes traffic to Pods that pass the readiness probe. Without one, traffic may arrive at your container before it has finished starting up, causing user-visible errors.",
        severity: "low",
      },
    ],
  },
];

const SEVERITY_DISPLAY = {
  high: {
    label: "Error",
    className: "text-danger border-danger/30 bg-danger-muted",
    dot: "bg-danger",
  },
  medium: {
    label: "Warning",
    className: "text-warning border-warning/30 bg-warning-muted",
    dot: "bg-warning",
  },
  low: {
    label: "Warning",
    className: "text-warning/70 border-warning/20 bg-warning-muted/50",
    dot: "bg-warning/60",
  },
  info: {
    label: "Info",
    className: "text-accent border-accent/30 bg-accent-muted",
    dot: "bg-accent",
  },
};

export function RuleCatalogPage() {
  return (
    <div className="min-h-full bg-surface-950">
      <header className="border-b border-surface-border bg-surface-900/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <a href="/" className="flex items-center gap-2.5 group">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-muted text-accent">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
                </svg>
              </div>
              <div>
                <h1 className="text-sm font-semibold leading-none text-neutral-100 group-hover:text-accent transition-colors">KubePilot</h1>
                <p className="mt-1 text-xs leading-none text-neutral-500">Kubernetes manifest validator</p>
              </div>
            </a>
          </div>
          <div className="flex items-center gap-5">
            <a href="/" className="text-xs text-neutral-500 transition-colors hover:text-neutral-300">
              Validator
            </a>
            <a
              href="https://kubernetes.io/docs/concepts/overview/working-with-objects/"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-neutral-500 transition-colors hover:text-neutral-300"
            >
              K8s reference ↗
            </a>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-10">
          <h2 className="text-2xl font-semibold text-neutral-100">Rule Catalog</h2>
          <p className="mt-2 text-sm text-neutral-500 max-w-lg">
            Every check KubePilot runs, in plain English. Errors block a valid response; warnings
            are best-practice recommendations that won't cause kubectl to reject the manifest.
          </p>
        </div>

        <div className="space-y-10">
          {CATALOG.map((category) => (
            <section key={category.title}>
              <div className="mb-4">
                <h3 className="text-base font-semibold text-neutral-100">{category.title}</h3>
                <p className="mt-1 text-xs text-neutral-500">{category.description}</p>
              </div>
              <div className="space-y-3">
                {category.rules.map((rule) => {
                  const s = SEVERITY_DISPLAY[rule.severity];
                  return (
                    <div
                      key={rule.name}
                      className="rounded-xl border border-surface-border bg-surface-850 p-4"
                    >
                      <div className="flex flex-wrap items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-1.5">
                            <span className="text-sm font-medium text-neutral-100">{rule.name}</span>
                            <span
                              className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium ${s.className}`}
                            >
                              <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
                              {s.label}
                            </span>
                            {rule.kinds?.map((k) => (
                              <span
                                key={k}
                                className="rounded-full bg-surface-700 px-2 py-0.5 text-[11px] font-mono text-neutral-500"
                              >
                                {k}
                              </span>
                            ))}
                          </div>
                          <p className="text-sm text-neutral-400 leading-relaxed">{rule.why}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>

        <div className="mt-12 rounded-xl border border-surface-border bg-surface-850 p-5">
          <p className="text-sm text-neutral-400">
            <span className="font-medium text-neutral-200">Is a rule missing or wrong?</span>
            {" "}KubePilot aims for a small, accurate, well-explained rule set rather than the
            largest possible one. If you've found a genuine mistake or a common Kubernetes gotcha
            that's not covered, the project welcomes feedback.
          </p>
        </div>
      </main>
    </div>
  );
}
