import axios from "axios";

// Set VITE_API_BASE_URL in Netlify's env vars to your Render backend URL,
// e.g. https://kubepilot-api.onrender.com. Falls back to local dev.
const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  timeout: 15_000,
  headers: {
    "Content-Type": "application/json",
  },
});
