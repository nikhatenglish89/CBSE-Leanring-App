import { useState } from "react";

import { PageHeader } from "../../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Select, useToast } from "../../components/ui";
import { useAdminFeedback, useUpdateFeedbackStatus } from "../../hooks/useFeedback";
import { formatDateTime } from "../../lib/format";
import type { FeedbackStatus } from "../../types/feedback";

const CATEGORY_LABEL: Record<string, string> = {
  BUG: "Bug report",
  SUGGESTION: "Suggestion",
  GENERAL: "General feedback",
};

const STATUS_TONE: Record<FeedbackStatus, "warning" | "brand" | "success"> = {
  NEW: "warning",
  REVIEWED: "brand",
  RESOLVED: "success",
};

const STATUS_TABS: { value: FeedbackStatus | ""; label: string }[] = [
  { value: "", label: "All" },
  { value: "NEW", label: "New" },
  { value: "REVIEWED", label: "Reviewed" },
  { value: "RESOLVED", label: "Resolved" },
];

export function AdminFeedbackPage() {
  const [statusTab, setStatusTab] = useState<FeedbackStatus | "">("");
  const [category, setCategory] = useState("");
  const { data: feedback, isLoading } = useAdminFeedback({ status: statusTab, category });
  const updateStatus = useUpdateFeedbackStatus();
  const { showToast } = useToast();

  const onSetStatus = async (feedbackId: string, status: FeedbackStatus) => {
    try {
      await updateStatus.mutateAsync({ feedbackId, status });
    } catch {
      showToast("Could not update that feedback's status.", "error");
    }
  };

  return (
    <div className="page-shell flex flex-col gap-6 py-10">
      <PageHeader
        eyebrow="Admin"
        title="User Feedback"
        subtitle="Bug reports, suggestions, and general feedback submitted by students, teachers, and parents."
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.value}
              type="button"
              onClick={() => setStatusTab(tab.value)}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
                statusTab === tab.value ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="w-48">
          <Select label="Category" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            <option value="BUG">Bug reports</option>
            <option value="SUGGESTION">Suggestions</option>
            <option value="GENERAL">General feedback</option>
          </Select>
        </div>
      </div>

      {isLoading && <CardSkeleton />}

      {!isLoading && feedback && feedback.length > 0 && (
        <div className="flex flex-col gap-4">
          {feedback.map((item) => (
            <Card key={item.id} className="flex flex-col gap-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="font-medium text-slate-900">
                    {item.user_name} <span className="text-slate-400">&middot;</span>{" "}
                    <span className="text-sm text-slate-500">{item.user_email}</span>
                  </p>
                  <p className="text-xs text-slate-500">
                    {item.user_role} &middot; {formatDateTime(item.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone="neutral">{CATEGORY_LABEL[item.category]}</Badge>
                  <Badge tone={STATUS_TONE[item.status]}>{item.status}</Badge>
                </div>
              </div>
              <p className="whitespace-pre-wrap text-sm text-slate-700">{item.message}</p>
              <div className="flex gap-2">
                {item.status !== "REVIEWED" && (
                  <Button
                    variant="secondary"
                    isLoading={updateStatus.isPending}
                    onClick={() => onSetStatus(item.id, "REVIEWED")}
                  >
                    Mark reviewed
                  </Button>
                )}
                {item.status !== "RESOLVED" && (
                  <Button isLoading={updateStatus.isPending} onClick={() => onSetStatus(item.id, "RESOLVED")}>
                    Mark resolved
                  </Button>
                )}
                {item.status !== "NEW" && (
                  <Button
                    variant="ghost"
                    isLoading={updateStatus.isPending}
                    onClick={() => onSetStatus(item.id, "NEW")}
                  >
                    Reopen
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && feedback?.length === 0 && (
        <EmptyState icon="📭" title="No feedback here" description="Nothing matches the current filters." />
      )}
    </div>
  );
}
