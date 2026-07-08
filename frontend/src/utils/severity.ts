import type { Severity } from "@/types";

export interface SeverityStyle {
  label: string;
  textClass: string;
  bgClass: string;
  borderClass: string;
  dotClass: string;
}

const SEVERITY_STYLES: Record<Severity, SeverityStyle> = {
  high: {
    label: "High",
    textClass: "text-danger",
    bgClass: "bg-danger-muted",
    borderClass: "border-danger/30",
    dotClass: "bg-danger",
  },
  medium: {
    label: "Medium",
    textClass: "text-warning",
    bgClass: "bg-warning-muted",
    borderClass: "border-warning/30",
    dotClass: "bg-warning",
  },
  low: {
    label: "Low",
    textClass: "text-neutral-400",
    bgClass: "bg-surface-700",
    borderClass: "border-surface-border",
    dotClass: "bg-neutral-500",
  },
};

export function getSeverityStyle(severity: Severity): SeverityStyle {
  return SEVERITY_STYLES[severity];
}

export function getScoreColor(score: number): string {
  if (score >= 85) return "text-success";
  if (score >= 60) return "text-warning";
  return "text-danger";
}
