import { useMutation } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ChatMessage, ChatResponse } from "../types/assistant";
import type { ApiSuccess } from "../types/auth";

export function useAssistantChat() {
  return useMutation({
    mutationFn: async ({ message, history }: { message: string; history: ChatMessage[] }) => {
      const { data } = await api.post<ApiSuccess<ChatResponse>>("/assistant/chat", { message, history });
      return data.data;
    },
  });
}
