export type UserRole = "STUDENT" | "PARENT" | "TEACHER" | "ADMIN" | "SUPER_ADMIN" | "SUPPORT_AGENT" | "CONTENT_MANAGER";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  status: string;
  role: UserRole;
  email_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiSuccess<T> {
  success: true;
  data: T;
  meta?: { page: number; page_size: number; total: number };
}

export interface ApiError {
  success: false;
  error: { code: string; message: string };
}
