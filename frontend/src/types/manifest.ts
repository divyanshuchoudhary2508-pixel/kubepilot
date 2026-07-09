export type Severity = "high" | "medium" | "low";

export interface Issue {
  line: number | null;
  severity: Severity;
  title: string;
  message: string;
  suggestion: string | null;
  /** 0-indexed document position in a multi-doc YAML stream. Null for single-doc. */
  document_index: number | null;
}

export interface ValidationResponse {
  valid: boolean;
  errors: Issue[];
  warnings: Issue[];
  passed_checks: string[];
  score: number;
  /** Number of YAML documents that were validated */
  document_count: number;
}

export interface FixResponse {
  fixed_content: string;
  applied_fixes: string[];
}

export interface ManifestRequest {
  content: string;
}
