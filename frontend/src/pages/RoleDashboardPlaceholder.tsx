import { Card } from "../components/ui";
import { useAuth } from "../hooks/useAuth";

export function RoleDashboardPlaceholder({ roleLabel }: { roleLabel: string }) {
  const { user } = useAuth();

  return (
    <div className="page-shell py-12">
      <Card className="mx-auto flex max-w-xl flex-col items-center gap-3 py-12 text-center">
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 text-2xl">
          🚧
        </span>
        <h1 className="text-xl font-semibold text-slate-900">
          Welcome, {user?.full_name ?? "…"}
        </h1>
        <p className="max-w-sm text-sm text-slate-600">
          The {roleLabel.toLowerCase()} dashboard is coming in a later phase. Authentication and
          role routing already work end-to-end — this page just proves it.
        </p>
      </Card>
    </div>
  );
}
