export type FeedbackCategory = "BUG" | "SUGGESTION" | "GENERAL";
export type FeedbackStatus = "NEW" | "REVIEWED" | "RESOLVED";

export interface Feedback {
  id: string;
  category: FeedbackCategory;
  message: string;
  status: FeedbackStatus;
  created_at: string;
}

export interface AdminFeedback extends Feedback {
  user_name: string;
  user_email: string;
  user_role: string;
}
