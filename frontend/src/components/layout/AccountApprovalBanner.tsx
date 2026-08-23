import { useAuth } from "../../hooks/useAuth";

export function AccountApprovalBanner() {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user || user.is_verified) return null;
  if (user.role !== "STUDENT" && user.role !== "TEACHER") return null;

  const message =
    user.role === "TEACHER"
      ? "You can build courses as drafts, but you'll need to be verified before you can publish."
      : "You can see free content for now — verification unlocks paid content too.";

  return (
    <div className="border-b border-blue-200 bg-blue-50">
      <div className="page-shell flex items-center justify-center py-2.5 text-center text-sm text-blue-800">
        <p>
          <span className="font-medium">Account pending admin approval.</span> {message}
        </p>
      </div>
    </div>
  );
}
