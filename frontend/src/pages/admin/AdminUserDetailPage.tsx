import { useNavigate, useParams } from "react-router-dom";

import { Badge, Card, CardSkeleton } from "../../components/ui";
import { useAdminUserDetail } from "../../hooks/useAdminUsers";
import type { UserRole } from "../../types/users";

const ROLE_LABEL: Partial<Record<UserRole, string>> = {
  STUDENT: "Student",
  TEACHER: "Teacher",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
};

export function AdminUserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { data: detail, isLoading } = useAdminUserDetail(userId);

  if (isLoading || !detail) {
    return (
      <div className="page-shell flex flex-col gap-4 py-10">
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="page-shell mx-auto flex max-w-2xl flex-col gap-6 py-10">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="self-start text-sm font-medium text-brand-600 hover:underline"
      >
        &larr; Back
      </button>

      <Card className="flex flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="brand">{ROLE_LABEL[detail.role] ?? detail.role}</Badge>
          <Badge tone={detail.status === "ACTIVE" ? "success" : "neutral"}>{detail.status}</Badge>
          {detail.email_verified ? (
            <Badge tone="success">Email verified</Badge>
          ) : (
            <Badge tone="warning">Email not verified</Badge>
          )}
          {detail.must_reset_password && <Badge tone="warning">Password reset pending</Badge>}
        </div>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">{detail.full_name}</h1>
        <p className="text-sm text-slate-500">{detail.email}</p>
        {detail.phone && <p className="text-sm text-slate-500">{detail.phone}</p>}
      </Card>

      {detail.role === "STUDENT" && (
        <Card className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Student profile</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-slate-500">Class</p>
              <p className="font-medium text-slate-800">{detail.current_class_name ?? "Not assigned yet"}</p>
            </div>
            <div>
              <p className="text-slate-500">Date of birth</p>
              <p className="font-medium text-slate-800">{detail.date_of_birth ?? "Not set"}</p>
            </div>
          </div>
        </Card>
      )}

      {detail.role === "TEACHER" && (
        <Card className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Teacher profile</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-slate-500">Verified</p>
              <p className="font-medium text-slate-800">{detail.teacher_verified ? "Yes" : "No"}</p>
            </div>
            <div>
              <p className="text-slate-500">Courses created</p>
              <p className="font-medium text-slate-800">{detail.course_count ?? 0}</p>
            </div>
          </div>
          {detail.bio && (
            <div className="text-sm">
              <p className="text-slate-500">Bio</p>
              <p className="text-slate-800">{detail.bio}</p>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
