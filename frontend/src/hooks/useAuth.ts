import { useMutation } from "@tanstack/react-query";

import { api } from "../lib/api";
import { useAuthStore } from "../store/authStore";
import type { ApiSuccess, AuthTokens, User } from "../types/auth";

interface LoginPayload {
  email: string;
  password: string;
}

interface RegisterPayload extends LoginPayload {
  full_name: string;
  role: "STUDENT" | "PARENT" | "TEACHER";
}

async function fetchMe(): Promise<User> {
  const { data } = await api.get<ApiSuccess<User>>("/users/me");
  return data.data;
}

export function useAuth() {
  const { user, accessToken, setSession, clearSession } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const { data } = await api.post<ApiSuccess<AuthTokens>>("/auth/login", payload);
      return data.data;
    },
    onSuccess: async (tokens) => {
      useAuthStore.getState().setAccessToken(tokens.access_token);
      const me = await fetchMe();
      setSession(me, tokens);
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      await api.post<ApiSuccess<User>>("/auth/register", payload);
      // Registration doesn't log the user in automatically — a distinct,
      // explicit login keeps the auth flow's mental model simple.
      return loginMutation.mutateAsync({ email: payload.email, password: payload.password });
    },
  });

  const logout = () => {
    const refreshToken = useAuthStore.getState().refreshToken;
    if (refreshToken) {
      api.post("/auth/logout", { refresh_token: refreshToken }).catch(() => {
        // Logout is best-effort client-side: the token is discarded locally
        // regardless of whether the server-side revoke call succeeds.
      });
    }
    clearSession();
  };

  return {
    user,
    isAuthenticated: Boolean(user && accessToken),
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout,
  };
}
