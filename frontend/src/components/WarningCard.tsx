import type { Issue } from "@/types";
import { IssueCard } from "./IssueCard";

interface WarningCardProps {
  issue: Issue;
}

export function WarningCard({ issue }: WarningCardProps) {
  return <IssueCard issue={issue} />;
}
