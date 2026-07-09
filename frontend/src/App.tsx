import { HomePage, RuleCatalogPage } from "@/pages";

/**
 * Simple path-based routing without a router dependency.
 * Only two routes exist: / (HomePage) and /rules (RuleCatalogPage).
 */
export function App() {
  const path = window.location.pathname;

  if (path === "/rules") {
    return <RuleCatalogPage />;
  }

  return <HomePage />;
}
