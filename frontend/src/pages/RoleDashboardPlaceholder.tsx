import { Card } from "../components/ui";
import { useAuth } from "../hooks/useAuth";

export function RoleDashboardPlaceholder({ roleLabel }: { roleLabel: string }) {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <Card>
        <h1 className="text-xl font-semibold text-slate-900">
          Logged in as {user?.full_name ?? "…"} ({roleLabel})
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          The {roleLabel.toLowerCase()} dashboard is coming in a later phase. Authentication and
          role routing are working — this page just proves it.
        </p>
      </Card>
    </div>
  );
}
