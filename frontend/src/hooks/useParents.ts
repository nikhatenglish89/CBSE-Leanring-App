import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { ChildProgress } from "../types/parents";

// No WebSocket infrastructure in this app — short-interval polling gives
// parents a "live" progress view within the existing REST setup, same
// pattern as messaging's near-real-time polling.
const CHILDREN_POLL_MS = 15_000;

export function useChildrenProgress() {
  return useQuery({
    queryKey: ["children-progress"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<ChildProgress[]>>("/parents/children");
      return data.data;
    },
    refetchInterval: CHILDREN_POLL_MS,
  });
}
