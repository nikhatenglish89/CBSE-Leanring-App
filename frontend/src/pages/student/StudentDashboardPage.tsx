import { Card } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";

export function StudentDashboardPage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <Card>
        <h1 className="text-xl font-semibold text-slate-900">
          Logged in as {user?.full_name ?? "…"}
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          This is a placeholder student dashboard proving the authentication flow end-to-end.
          Courses, progress, and tests land in later phases.
        </p>
      </Card>
    </div>
  );
}
