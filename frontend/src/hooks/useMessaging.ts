import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { Conversation, Message, MessageableUser } from "../types/messaging";

/** No WebSocket infrastructure in this app (see HLD) — polling on a short
 * interval gives a near-real-time feel within the existing REST setup. */
const CONVERSATIONS_POLL_MS = 8_000;
const MESSAGES_POLL_MS = 4_000;

export function useConversations() {
  return useQuery({
    queryKey: ["conversations"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Conversation[]>>("/conversations");
      return data.data;
    },
    refetchInterval: CONVERSATIONS_POLL_MS,
  });
}

export function useMessageableUsers(search: string) {
  return useQuery({
    queryKey: ["messageable-users", search],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<MessageableUser[]>>("/conversations/messageable-users", {
        params: { search: search || undefined },
      });
      return data.data;
    },
  });
}

export function useStartConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (otherUserId: string) => {
      const { data } = await api.post<ApiSuccess<Conversation>>("/conversations", {
        other_user_id: otherUserId,
      });
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["conversations"] }),
  });
}

export function useMessages(conversationId: string | undefined) {
  return useQuery({
    queryKey: ["messages", conversationId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Message[]>>(
        `/conversations/${conversationId}/messages`,
        { params: { page_size: 100 } }
      );
      return data.data;
    },
    enabled: Boolean(conversationId),
    refetchInterval: MESSAGES_POLL_MS,
  });
}

export function useSendMessage(conversationId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: string) => {
      const { data } = await api.post<ApiSuccess<Message>>(
        `/conversations/${conversationId}/messages`,
        { body }
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages", conversationId] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}
