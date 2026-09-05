import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Badge, Button, Card, CardSkeleton, Spinner, useToast } from "../../components/ui";
import {
  useAdminUserDetail,
  useAdminUsers,
  useLinkParent,
  useUnlinkParent,
  useUnverifyUser,
  useVerifyUser,
} from "../../hooks/useAdminUsers";
import type { UserRole } from "../../types/users";

const ROLE_LABEL: Partial<Record<UserRole, string>> = {
  STUDENT: "Student",
  TEACHER: "Teacher",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
};

const APPROVAL_ROLES: UserRole[] = ["STUDENT", "TEACHER"];

function LinkParentCard({ studentId }: { studentId: string }) {
  const [search, setSearch] = useState("");
  const { data: candidates, isLoading } = useAdminUsers({ role: "PARENT", search });
  const linkParent = useLinkParent(studentId);
  const { showToast } = useToast();

  const onPick = async (parentUserId: string) => {
    try {
      await linkParent.mutateAsync(parentUserId);
      setSearch("");
      showToast("Parent linked — they'll now see this student's progress.", "success");
    } catch {
      showToast("Could not link that parent account.", "error");
    }
  };

  return (
    <Card className="flex flex-col gap-3">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Link a parent</h2>
        <p className="mt-1 text-sm text-slate-500">
          Linking connects this student's practice test progress to a parent's dashboard.
        </p>
      </div>
      <input
        placeholder="Search parent by name or email..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
      />
      <div className="flex max-h-52 flex-col gap-1 overflow-y-auto">
        {isLoading && <Spinner className="mx-auto my-2" />}
        {!isLoading && candidates?.length === 0 && (
          <p className="py-2 text-center text-sm text-slate-500">
            {search ? "No matching parent accounts found." : "Type to search parent accounts."}
          </p>
        )}
        {candidates?.map((candidate) => (
          <button
            key={candidate.id}
            type="button"
            onClick={() => onPick(candidate.id)}
            disabled={linkParent.isPending}
            className="flex items-center justify-between rounded-lg px-2 py-2 text-left text-sm hover:bg-slate-50 disabled:opacity-50"
          >
            <span>
              <span className="font-medium text-slate-900">{candidate.full_name}</span>{" "}
              <span className="text-slate-500">&middot; {candidate.email}</span>
            </span>
            <span className="text-xs font-medium text-brand-600">Link</span>
          </button>
        ))}
      </div>
    </Card>
  );
}

export function AdminUserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { data: detail, isLoading } = useAdminUserDetail(userId);
  const verifyUser = useVerifyUser();
  const unverifyUser = useUnverifyUser();
  const unlinkParent = useUnlinkParent(userId ?? "");
  const { showToast } = useToast();

  if (isLoading || !detail) {
    return (
      <div className="page-shell flex flex-col gap-4 py-10">
        <CardSkeleton />
      </div>
    );
  }

  const onVerify = async () => {
    try {
      await verifyUser.mutateAsync(detail.id);
      showToast("Account verified.", "success");
    } catch {
      showToast("Could not verify this account.", "error");
    }
  };

  const onUnverify = async () => {
    try {
      await unverifyUser.mutateAsync(detail.id);
      showToast("Verification revoked.", "success");
    } catch {
      showToast("Could not update this account.", "error");
    }
  };

  const onUnlinkParent = async () => {
    try {
      await unlinkParent.mutateAsync();
      showToast("Parent unlinked.", "success");
    } catch {
      showToast("Could not unlink this parent.", "error");
    }
  };

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

      {APPROVAL_ROLES.includes(detail.role) && (
        <Card className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Account approval</h2>
              <p className="mt-1 text-sm text-slate-500">
                {detail.role === "TEACHER"
                  ? "A teacher can only publish courses once their account is verified."
                  : "An unverified student only sees free published content — verify to unlock paid content too."}
              </p>
            </div>
            <Badge tone={detail.is_verified ? "success" : "warning"}>
              {detail.is_verified ? "Verified" : "Pending approval"}
            </Badge>
          </div>
          {detail.is_verified ? (
            <Button variant="secondary" onClick={onUnverify} isLoading={unverifyUser.isPending} className="w-fit">
              Revoke verification
            </Button>
          ) : (
            <Button onClick={onVerify} isLoading={verifyUser.isPending} className="w-fit">
              Verify account
            </Button>
          )}
        </Card>
      )}

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

      {detail.role === "STUDENT" &&
        (detail.linked_parent ? (
          <Card className="flex flex-col gap-3">
            <h2 className="text-lg font-semibold text-slate-900">Linked parent</h2>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-sm">
                <p className="font-medium text-slate-800">{detail.linked_parent.full_name}</p>
                <p className="text-slate-500">{detail.linked_parent.email}</p>
              </div>
              <Button
                variant="secondary"
                onClick={onUnlinkParent}
                isLoading={unlinkParent.isPending}
                className="w-fit"
              >
                Unlink
              </Button>
            </div>
          </Card>
        ) : (
          <LinkParentCard studentId={detail.id} />
        ))}

      {detail.role === "TEACHER" && (
        <Card className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Teacher profile</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
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
