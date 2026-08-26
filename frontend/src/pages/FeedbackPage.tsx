import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Select, Textarea, useToast } from "../components/ui";
import { useMyFeedback, useSubmitFeedback } from "../hooks/useFeedback";
import { formatDateTime } from "../lib/format";
import type { FeedbackStatus } from "../types/feedback";

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

const STATUS_LABEL: Record<FeedbackStatus, string> = {
  NEW: "Received",
  REVIEWED: "Being reviewed",
  RESOLVED: "Resolved",
};

const schema = z.object({
  category: z.enum(["BUG", "SUGGESTION", "GENERAL"]),
  message: z.string().min(1, "Please write a message").max(4000),
});

type FormValues = z.infer<typeof schema>;

export function FeedbackPage() {
  const { data: myFeedback, isLoading } = useMyFeedback();
  const submitFeedback = useSubmitFeedback();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { category: "GENERAL" } });

  const onSubmit = async (values: FormValues) => {
    try {
      await submitFeedback.mutateAsync(values);
      reset({ category: "GENERAL", message: "" });
      showToast("Thanks — your feedback has been sent to the team.", "success");
    } catch {
      showToast("Could not send your feedback — please try again.", "error");
    }
  };

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Feedback"
        title="Give feedback"
        subtitle="Found a bug, have an idea, or just want to tell us something? We read every submission."
      />

      <Card className="flex flex-col gap-4">
        <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
          <Select label="What's this about?" {...register("category")}>
            <option value="GENERAL">General feedback</option>
            <option value="BUG">Bug report</option>
            <option value="SUGGESTION">Suggestion</option>
          </Select>
          <Textarea
            label="Your message"
            rows={5}
            placeholder="Tell us what's on your mind..."
            error={errors.message?.message}
            {...register("message")}
          />
          <Button type="submit" isLoading={submitFeedback.isPending} className="self-start">
            Send feedback
          </Button>
        </form>
      </Card>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Your previous feedback</h2>
        {isLoading && <CardSkeleton />}
        {!isLoading && myFeedback && myFeedback.length > 0 && (
          <ul className="flex flex-col divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
            {myFeedback.map((item) => (
              <li key={item.id} className="flex flex-col gap-2 px-5 py-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    {CATEGORY_LABEL[item.category]}
                  </span>
                  <div className="flex items-center gap-2">
                    <Badge tone={STATUS_TONE[item.status]}>{STATUS_LABEL[item.status]}</Badge>
                    <span className="text-xs text-slate-400">{formatDateTime(item.created_at)}</span>
                  </div>
                </div>
                <p className="whitespace-pre-wrap text-sm text-slate-700">{item.message}</p>
              </li>
            ))}
          </ul>
        )}
        {!isLoading && myFeedback?.length === 0 && (
          <EmptyState icon="📝" title="No feedback yet" description="Anything you send will show up here." />
        )}
      </div>
    </div>
  );
}
