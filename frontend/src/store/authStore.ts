import { create } from "zustand";

import type { AuthTokens, User } from "../types/auth";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (user: User, tokens: AuthTokens) => void;
  setAccessToken: (accessToken: string) => void;
  clearSession: () => void;
}

/**
 * Client-only session snapshot. Deliberately minimal (per
 * docs/ARCHITECTURE.md §7): everything else lives in TanStack Query.
 * The access token is held in memory only — never persisted to
 * localStorage/sessionStorage — to keep it out of reach of XSS.
 */
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  setSession: (user, tokens) =>
    set({ user, accessToken: tokens.access_token, refreshToken: tokens.refresh_token }),
  setAccessToken: (accessToken) => set({ accessToken }),
  clearSession: () => set({ user: null, accessToken: null, refreshToken: null }),
}));
