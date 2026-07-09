import { Compass } from "lucide-react";

const isRuleCatalog = typeof window !== "undefined" && window.location.pathname === "/rules";

export function Navbar() {
  return (
    <header className="border-b border-surface-border bg-surface-900/80 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <a href="/" className="flex items-center gap-2.5 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-muted text-accent">
            <Compass size={18} strokeWidth={2.25} />
          </div>
          <div>
            <h1 className="text-sm font-semibold leading-none text-neutral-100 group-hover:text-accent transition-colors">
              KubePilot
            </h1>
            <p className="mt-1 text-xs leading-none text-neutral-500">Kubernetes manifest validator</p>
          </div>
        </a>

        <nav className="flex items-center gap-5">
          <a
            href="/rules"
            className={`text-xs transition-colors ${
              isRuleCatalog
                ? "text-accent font-medium"
                : "text-neutral-500 hover:text-neutral-300"
            }`}
          >
            Rule Catalog
          </a>
          <a
            href="https://kubernetes.io/docs/concepts/overview/working-with-objects/"
            target="_blank"
            rel="noreferrer"
            className="text-xs text-neutral-500 transition-colors hover:text-neutral-300"
          >
            K8s reference ↗
          </a>
        </nav>
      </div>
    </header>
  );
}
