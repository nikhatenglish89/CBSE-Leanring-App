import axios from "axios";

import { useAuthStore } from "../store/authStore";
import type { AuthTokens } from "../types/auth";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshInFlight: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = useAuthStore.getState().refreshToken;
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }
  const { data } = await api.post<{ data: AuthTokens }>("/auth/refresh", { refresh_token: refreshToken });
  useAuthStore.getState().setSession(useAuthStore.getState().user!, data.data);
  return data.data.access_token;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    // Silent-refresh-on-401, exactly once per request, per docs/ARCHITECTURE.md §7.
    // Must exclude /auth/refresh itself — otherwise a 401 there (an
    // expired/invalid stored refresh token) re-enters this same handler,
    // which awaits `refreshInFlight` while that very call is what has to
    // settle it: a deadlocked promise that never resolves, leaving
    // useAuthBootstrap's request hanging forever and the whole app stuck
    // on the loading spinner. A failed refresh should just fail.
    const isRefreshCall = typeof original.url === "string" && original.url.includes("/auth/refresh");
    if (status === 401 && !isRefreshCall && !original._retried && useAuthStore.getState().refreshToken) {
      original._retried = true;
      try {
        refreshInFlight ??= refreshAccessToken();
        const newAccessToken = await refreshInFlight;
        refreshInFlight = null;
        original.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(original);
      } catch {
        refreshInFlight = null;
        useAuthStore.getState().clearSession();
      }
    }
    return Promise.reject(error);
  }
);
