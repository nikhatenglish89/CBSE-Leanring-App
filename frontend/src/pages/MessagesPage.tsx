import { useEffect, useRef, useState } from "react";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Button, EmptyState, Spinner, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import {
  useConversations,
  useMessageableUsers,
  useMessages,
  useSendMessage,
  useStartConversation,
} from "../hooks/useMessaging";
import { formatDateTime } from "../lib/format";

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  const first = parts[0]?.[0] ?? "";
  const last = parts.length > 1 ? parts[parts.length - 1]?.[0] ?? "" : "";
  return (first + last).toUpperCase();
}

function NewChatPanel({ onStarted, onClose }: { onStarted: (conversationId: string) => void; onClose: () => void }) {
  const { user } = useAuth();
  const [search, setSearch] = useState("");
  const { data: candidates, isLoading } = useMessageableUsers(search);
  const startConversation = useStartConversation();
  const { showToast } = useToast();

  const counterpartLabel = user?.role === "STUDENT" ? "a teacher" : "a student";

  const onPick = async (userId: string) => {
    try {
      const conversation = await startConversation.mutateAsync(userId);
      onStarted(conversation.id);
    } catch {
      showToast("Could not start that conversation.", "error");
    }
  };

  return (
    <div className="flex flex-col gap-3 border-b border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-800">Message {counterpartLabel}</p>
        <button type="button" onClick={onClose} className="text-sm text-slate-500 hover:text-slate-700">
          Cancel
        </button>
      </div>
      <input
        autoFocus
        placeholder="Search by name..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
      />
      <div className="flex max-h-56 flex-col gap-1 overflow-y-auto">
        {isLoading && <Spinner className="mx-auto my-2" />}
        {!isLoading && candidates?.length === 0 && (
          <p className="py-2 text-center text-sm text-slate-500">
            No {counterpartLabel === "a teacher" ? "verified teachers" : "students"} found.
          </p>
        )}
        {candidates?.map((candidate) => (
          <button
            key={candidate.id}
            type="button"
            onClick={() => onPick(candidate.id)}
            disabled={startConversation.isPending}
            className="flex items-center gap-2 rounded-lg px-2 py-2 text-left text-sm hover:bg-white disabled:opacity-50"
          >
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
              {initials(candidate.full_name)}
            </span>
            {candidate.full_name}
          </button>
        ))}
      </div>
    </div>
  );
}

function MessageThread({ conversationId, otherName }: { conversationId: string; otherName: string }) {
  const { user } = useAuth();
  const { data: messages, isLoading } = useMessages(conversationId);
  const sendMessage = useSendMessage(conversationId);
  const { showToast } = useToast();
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages?.length]);

  const onSend = async (event: React.FormEvent) => {
    event.preventDefault();
    const body = draft.trim();
    if (!body) return;
    setDraft("");
    try {
      await sendMessage.mutateAsync(body);
    } catch {
      showToast("Could not send — please try again.", "error");
      setDraft(body);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 px-4 py-3">
        <p className="font-semibold text-slate-900">{otherName}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {isLoading && <Spinner className="mx-auto" />}
        {!isLoading && messages?.length === 0 && (
          <p className="mt-8 text-center text-sm text-slate-500">
            No messages yet — say hello to start the conversation.
          </p>
        )}
        <div className="flex flex-col gap-3">
          {messages?.map((message) => {
            const mine = message.sender_id === user?.id;
            return (
              <div key={message.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${
                    mine ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-800"
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{message.body}</p>
                  <p className={`mt-1 text-[11px] ${mine ? "text-brand-100" : "text-slate-400"}`}>
                    {formatDateTime(message.created_at)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
        <div ref={bottomRef} />
      </div>

      <form onSubmit={onSend} className="flex items-end gap-2 border-t border-slate-200 p-3">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSend(event);
            }
          }}
          placeholder="Type a message..."
          rows={1}
          className="flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
        />
        <Button type="submit" isLoading={sendMessage.isPending} disabled={!draft.trim()}>
          Send
        </Button>
      </form>
    </div>
  );
}

export function MessagesPage() {
  const { data: conversations, isLoading } = useConversations();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showNewChat, setShowNewChat] = useState(false);

  const selected = conversations?.find((c) => c.id === selectedId);

  return (
    <div className="page-shell flex flex-col gap-6 py-10">
      <PageHeader
        eyebrow="Messages"
        title="Chat with teachers & students"
        subtitle="Direct conversations between students and teachers — replies usually show up within a few seconds."
      />

      <div className="grid overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card lg:grid-cols-[320px_1fr]">
        <div className="flex flex-col border-b border-slate-200 lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between border-b border-slate-200 p-4">
            <p className="font-semibold text-slate-900">Conversations</p>
            <Button variant="secondary" onClick={() => setShowNewChat((v) => !v)}>
              New chat
            </Button>
          </div>

          {showNewChat && (
            <NewChatPanel
              onStarted={(conversationId) => {
                setSelectedId(conversationId);
                setShowNewChat(false);
              }}
              onClose={() => setShowNewChat(false)}
            />
          )}

          <div className="max-h-[32rem] overflow-y-auto lg:max-h-[36rem]">
            {isLoading && <Spinner className="mx-auto my-6" />}
            {!isLoading && conversations?.length === 0 && !showNewChat && (
              <div className="p-4">
                <EmptyState
                  icon="💬"
                  title="No conversations yet"
                  description="Click New chat to message a teacher or student."
                />
              </div>
            )}
            {conversations?.map((conv) => (
              <button
                key={conv.id}
                type="button"
                onClick={() => setSelectedId(conv.id)}
                className={`flex w-full items-start gap-3 border-b border-slate-100 p-4 text-left transition-colors hover:bg-slate-50 ${
                  selectedId === conv.id ? "bg-brand-50" : ""
                }`}
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                  {initials(conv.other_user.full_name)}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate font-medium text-slate-900">{conv.other_user.full_name}</p>
                    {conv.unread_count > 0 && <Badge tone="brand">{conv.unread_count}</Badge>}
                  </div>
                  <p className="truncate text-sm text-slate-500">
                    {conv.last_message_preview ?? "No messages yet"}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="min-h-[24rem]">
          {selected ? (
            <MessageThread conversationId={selected.id} otherName={selected.other_user.full_name} />
          ) : (
            <div className="flex h-full items-center justify-center p-8 text-center text-sm text-slate-500">
              Select a conversation, or start a new one.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
