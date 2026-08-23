import { useEffect, useState } from "react";

import { api } from "../lib/api";
import { useAuthStore } from "../store/authStore";
import type { ApiSuccess, AuthTokens, User } from "../types/auth";

/**
 * Runs once on app load. If a refresh token survived from a previous
 * session (see authStore), exchanges it for a fresh access token and
 * re-fetches the current user so a page reload lands the user back where
 * they were instead of bouncing them to /login. Returns false while this
 * is in flight so the router doesn't render (and redirect from) protected
 * routes before the session is restored.
 */
export function useAuthBootstrap(): boolean {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const { refreshToken, user } = useAuthStore.getState();
    if (!refreshToken || user) {
      setIsReady(true);
      return;
    }

    (async () => {
      try {
        const { data: tokenData } = await api.post<ApiSuccess<AuthTokens>>("/auth/refresh", {
          refresh_token: refreshToken,
        });
        useAuthStore.getState().setAccessToken(tokenData.data.access_token);
        const { data: meData } = await api.get<ApiSuccess<User>>("/users/me");
        useAuthStore.getState().setSession(meData.data, tokenData.data);
      } catch {
        useAuthStore.getState().clearSession();
      } finally {
        setIsReady(true);
      }
    })();
  }, []);

  return isReady;
}
