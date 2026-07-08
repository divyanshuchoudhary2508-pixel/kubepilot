import { apiClient } from "./apiClient";
import type { FixResponse, ManifestRequest, ValidationResponse } from "@/types";

/**
 * Thrown when the backend is unreachable or returns a non-2xx response,
 * with a message already suitable for display in the UI.
 */
export class ManifestApiError extends Error {}

function toApiError(error: unknown, fallbackMessage: string): ManifestApiError {
  if (axiosIsError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return new ManifestApiError(detail);
    if (error.code === "ECONNABORTED") {
      return new ManifestApiError("The request timed out. Is the backend running?");
    }
    if (!error.response) {
      return new ManifestApiError("Could not reach the KubePilot backend.");
    }
  }
  return new ManifestApiError(fallbackMessage);
}

// Narrow, dependency-free axios error check (avoids importing axios's own
// isAxiosError just to keep this file's surface area small and explicit).
function axiosIsError(error: unknown): error is {
  response?: { data?: { detail?: unknown } };
  code?: string;
} {
  return typeof error === "object" && error !== null && "isAxiosError" in error;
}

export async function validateManifest(content: string): Promise<ValidationResponse> {
  try {
    const body: ManifestRequest = { content };
    const { data } = await apiClient.post<ValidationResponse>("/validate", body);
    return data;
  } catch (error) {
    throw toApiError(error, "Failed to validate the manifest.");
  }
}

export async function fixManifest(content: string): Promise<FixResponse> {
  try {
    const body: ManifestRequest = { content };
    const { data } = await apiClient.post<FixResponse>("/fix", body);
    return data;
  } catch (error) {
    throw toApiError(error, "Failed to fix the manifest.");
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    await apiClient.get("/health");
    return true;
  } catch {
    return false;
  }
}
