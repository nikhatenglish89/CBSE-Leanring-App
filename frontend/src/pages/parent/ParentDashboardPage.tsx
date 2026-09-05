import { PageHeader } from "../../components/layout/PageHeader";
import { Badge, Card, CardSkeleton, EmptyState } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";
import { useChildrenProgress } from "../../hooks/useParents";
import { formatDateTime } from "../../lib/format";
import type { ChildProgress } from "../../types/parents";

function scoreTone(pct: number): "success" | "warning" | "rose" {
  if (pct >= 75) return "success";
  if (pct >= 50) return "warning";
  return "rose";
}

function ChildCard({ child }: { child: ChildProgress }) {
  const hasScore = child.average_score_pct !== null;

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">{child.full_name}</h2>
          <p className="text-sm text-slate-500">
            {child.class_name ?? "Class not set"} &middot; {child.email}
          </p>
        </div>
        {hasScore && (
          <Badge tone={scoreTone(child.average_score_pct as number)}>
            {Math.round(child.average_score_pct as number)}% average
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 rounded-lg bg-slate-50 p-4 text-sm sm:grid-cols-3">
        <div>
          <p className="text-slate-500">Tests taken</p>
          <p className="text-xl font-semibold text-slate-900">{child.tests_taken}</p>
        </div>
        <div>
          <p className="text-slate-500">Average score</p>
          <p className="text-xl font-semibold text-slate-900">
            {hasScore ? `${Math.round(child.average_score_pct as number)}%` : "—"}
          </p>
        </div>
        <div className="col-span-2 sm:col-span-1">
          <p className="text-slate-500">Last active</p>
          <p className="text-sm font-medium text-slate-800">
            {child.last_activity_at ? formatDateTime(child.last_activity_at) : "No activity yet"}
          </p>
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Recent practice tests</h3>
        {child.recent_attempts.length === 0 ? (
          <p className="text-sm text-slate-500">No practice tests taken yet.</p>
        ) : (
          <ul className="flex flex-col divide-y divide-slate-100 overflow-hidden rounded-lg border border-slate-200">
            {child.recent_attempts.map((attempt) => (
              <li key={attempt.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5">
                <div>
                  <p className="text-sm font-medium text-slate-800">{attempt.practice_set_title}</p>
                  <p className="text-xs text-slate-500">
                    {attempt.subject_name} &middot; {attempt.class_name} &middot;{" "}
                    {formatDateTime(attempt.created_at)}
                  </p>
                </div>
                <Badge tone={scoreTone((attempt.score / attempt.total) * 100)}>
                  {attempt.score}/{attempt.total}
                </Badge>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}

export function ParentDashboardPage() {
  const { user } = useAuth();
  const { data: children, isLoading } = useChildrenProgress();

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <PageHeader
          eyebrow="Parent"
          title={`Welcome back, ${user?.full_name?.split(" ")[0] ?? "there"}`}
          subtitle="Live progress for every child linked to your account."
        />
        <span className="flex items-center gap-1.5 self-start rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" aria-hidden="true" />
          Live &middot; updates automatically
        </span>
      </div>

      {isLoading && (
        <div className="flex flex-col gap-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {!isLoading && children && children.length > 0 && (
        <div className="flex flex-col gap-6">
          {children.map((child) => (
            <ChildCard key={child.id} child={child} />
          ))}
        </div>
      )}

      {!isLoading && children?.length === 0 && (
        <EmptyState
          icon="👪"
          title="No children linked yet"
          description="Ask an admin to connect your account to your child's — once linked, their practice test progress will show up here automatically."
        />
      )}
    </div>
  );
}
