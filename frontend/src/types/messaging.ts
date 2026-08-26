export interface ConversationParticipant {
  id: string;
  full_name: string;
  role: string;
}

export interface Conversation {
  id: string;
  other_user: ConversationParticipant;
  last_message_preview: string | null;
  last_message_at: string | null;
  unread_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_name: string;
  body: string;
  created_at: string;
  read_at: string | null;
}

export interface MessageableUser {
  id: string;
  full_name: string;
}
