import { Download } from "lucide-react";
import { downloadTextFile } from "@/utils";

interface DownloadButtonProps {
  content: string;
  filename?: string;
}

export function DownloadButton({ content, filename = "fixed-manifest.yaml" }: DownloadButtonProps) {
  return (
    <button
      type="button"
      onClick={() => downloadTextFile(content, filename)}
      className="inline-flex items-center gap-2 rounded-xl border border-surface-border bg-surface-800 px-4 py-2 text-sm font-medium text-neutral-200 transition-colors hover:border-success/40 hover:text-success"
    >
      <Download size={15} />
      Download {filename}
    </button>
  );
}
