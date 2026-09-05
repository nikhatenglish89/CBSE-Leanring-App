import type { User, UserRole } from "./auth";

export type AdminCreatableRole = "STUDENT" | "TEACHER" | "ADMIN";

export interface AdminCreateUserPayload {
  email: string;
  full_name: string;
  phone?: string;
  role: AdminCreatableRole;
}

export interface AdminCreatedUserOut extends User {
  temporary_password: string;
}

export interface LinkedParent {
  id: string;
  full_name: string;
  email: string;
}

export interface UserDetailOut extends User {
  current_class_id: string | null;
  current_class_name: string | null;
  date_of_birth: string | null;
  bio: string | null;
  teacher_verified: boolean | null;
  student_verified: boolean | null;
  course_count: number | null;
  linked_parent: LinkedParent | null;
}

export type { User, UserRole };
