import { create } from "zustand";

import type { AuthTokens, User } from "../types/auth";

const REFRESH_TOKEN_KEY = "edusphere_refresh_token";

function loadStoredRefreshToken(): string | null {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

function persistRefreshToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(REFRESH_TOKEN_KEY, token);
    else localStorage.removeItem(REFRESH_TOKEN_KEY);
  } catch {
    // localStorage unavailable (private browsing, etc.) — session just
    // won't survive a page reload, same as before this change.
  }
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (user: User, tokens: AuthTokens) => void;
  setAccessToken: (accessToken: string) => void;
  updateUser: (user: User) => void;
  clearSession: () => void;
}

/**
 * Client-only session snapshot (per docs/ARCHITECTURE.md §7, everything
 * else lives in TanStack Query). The access token and user are held in
 * memory only and re-derived on every page load via useAuthBootstrap.
 * The refresh token is persisted to localStorage so a reload doesn't log
 * the user out — the architecture doc's ideal is an httpOnly cookie
 * instead (immune to JS entirely), which isn't implemented; the refresh
 * token was already round-tripping through frontend JS in the response
 * body before this change, so localStorage isn't a new exposure, just a
 * longer-lived one.
 */
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: loadStoredRefreshToken(),
  setSession: (user, tokens) => {
    persistRefreshToken(tokens.refresh_token);
    set({ user, accessToken: tokens.access_token, refreshToken: tokens.refresh_token });
  },
  setAccessToken: (accessToken) => set({ accessToken }),
  updateUser: (user) => set({ user }),
  clearSession: () => {
    persistRefreshToken(null);
    set({ user: null, accessToken: null, refreshToken: null });
  },
}));
