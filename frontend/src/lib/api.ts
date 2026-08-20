import axios from "axios";

import { useAuthStore } from "../store/authStore";
import type { AuthTokens } from "../types/auth";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
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
    if (status === 401 && !original._retried && useAuthStore.getState().refreshToken) {
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
