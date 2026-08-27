import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { Captcha } from "../types/captcha";

export function useCaptcha() {
  return useQuery({
    queryKey: ["captcha"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Captcha>>("/auth/captcha");
      return data.data;
    },
    staleTime: 0,
    gcTime: 0,
    refetchOnWindowFocus: false,
  });
}
