export type Severity = "high" | "medium" | "low";

export interface Issue {
  line: number | null;
  severity: Severity;
  title: string;
  message: string;
  suggestion: string | null;
}

export interface ValidationResponse {
  valid: boolean;
  errors: Issue[];
  warnings: Issue[];
  passed_checks: string[];
  score: number;
}

export interface FixResponse {
  fixed_content: string;
  applied_fixes: string[];
}

export interface ManifestRequest {
  content: string;
}
