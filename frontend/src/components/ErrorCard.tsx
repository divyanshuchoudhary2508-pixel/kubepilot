import type { Issue } from "@/types";
import { IssueCard } from "./IssueCard";

interface ErrorCardProps {
  issue: Issue;
}

export function ErrorCard({ issue }: ErrorCardProps) {
  return <IssueCard issue={issue} />;
}
