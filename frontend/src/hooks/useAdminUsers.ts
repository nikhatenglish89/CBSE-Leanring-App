import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { AdminCreatedUserOut, AdminCreateUserPayload, User, UserDetailOut } from "../types/users";

export function useAdminUsers(params: { role?: string; search?: string } = {}) {
  return useQuery({
    queryKey: ["admin-users", params],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<User[]>>("/users", {
        params: { role: params.role, search: params.search || undefined, page_size: 100 },
      });
      return data.data;
    },
  });
}

export function useAdminUserDetail(userId: string | undefined) {
  return useQuery({
    queryKey: ["admin-user-detail", userId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<UserDetailOut>>(`/users/${userId}`);
      return data.data;
    },
    enabled: Boolean(userId),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: AdminCreateUserPayload) => {
      const { data } = await api.post<ApiSuccess<AdminCreatedUserOut>>("/users", payload);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  });
}
