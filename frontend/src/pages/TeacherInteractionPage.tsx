import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Input, Select, Textarea, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { useClasses, useSubjects } from "../hooks/useCurriculum";
import {
  useBrowseLiveClasses,
  useBrowseQuestions,
  useCreateLiveClass,
  useDeleteLiveClass,
} from "../hooks/useInteraction";
import { formatDateTime } from "../lib/format";

const liveClassSchema = z.object({
  class_id: z.string().min(1, "Choose a class"),
  subject_id: z.string().min(1, "Choose a subject"),
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  scheduled_at: z.string().min(1, "Choose a date and time"),
  meeting_url: z.string().url("Enter a valid meeting link (e.g. a Zoom or Google Meet URL)"),
});

type LiveClassFormValues = z.infer<typeof liveClassSchema>;

function ScheduleLiveClassForm({ onDone }: { onDone: () => void }) {
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const createLiveClass = useCreateLiveClass();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<LiveClassFormValues>({ resolver: zodResolver(liveClassSchema) });

  const watchedClassId = watch("class_id");

  const onSubmit = async (values: LiveClassFormValues) => {
    try {
      await createLiveClass.mutateAsync({
        ...values,
        scheduled_at: new Date(values.scheduled_at).toISOString(),
      });
      showToast("Live class scheduled.", "success");
      onDone();
    } catch {
      showToast("Could not schedule the live class. Please try again.", "error");
    }
  };

  return (
    <Card className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-slate-900">Schedule a live class</h2>
      <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Select
          label="Class"
          error={errors.class_id?.message}
          {...register("class_id")}
          onChange={(event) => {
            setValue("class_id", event.target.value);
            setClassId(event.target.value);
          }}
        >
          <option value="">Select a class</option>
          {classes?.map((klass) => (
            <option key={klass.id} value={klass.id}>
              {klass.name}
            </option>
          ))}
        </Select>
        <Select label="Subject" error={errors.subject_id?.message} disabled={!watchedClassId} {...register("subject_id")}>
          <option value="">Select a subject</option>
          {subjects?.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.name}
            </option>
          ))}
        </Select>
        <Input
          label="Title"
          className="sm:col-span-2"
          placeholder="e.g. Doubt clearing — Trigonometry"
          error={errors.title?.message}
          {...register("title")}
        />
        <Textarea
          label="Description (optional)"
          className="sm:col-span-2"
          rows={2}
          {...register("description")}
        />
        <Input
          label="Date & time"
          type="datetime-local"
          error={errors.scheduled_at?.message}
          {...register("scheduled_at")}
        />
        <Input
          label="Meeting link"
          placeholder="https://meet.google.com/..."
          error={errors.meeting_url?.message}
          {...register("meeting_url")}
        />
        <div className="flex gap-2 sm:col-span-2">
          <Button type="submit" isLoading={createLiveClass.isPending}>
            Schedule
          </Button>
          <Button type="button" variant="secondary" onClick={onDone}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}

function LiveClassesSection() {
  const { user } = useAuth();
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const { data: liveClasses, isLoading } = useBrowseLiveClasses({
    classId: classId || undefined,
    subjectId: subjectId || undefined,
  });
  const deleteLiveClass = useDeleteLiveClass();
  const { showToast } = useToast();
  const [scheduling, setScheduling] = useState(false);

  const isTeacher = user?.role === "TEACHER";
  const now = Date.now();

  const onCancel = async (liveClassId: string) => {
    try {
      await deleteLiveClass.mutateAsync(liveClassId);
      showToast("Live class cancelled.", "success");
    } catch {
      showToast("Could not cancel this live class.", "error");
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-xl font-bold text-slate-900">Live classes</h2>
        {isTeacher && !scheduling && (
          <Button onClick={() => setScheduling(true)}>Schedule a live class</Button>
        )}
      </div>

      {scheduling && <ScheduleLiveClassForm onDone={() => setScheduling(false)} />}

      <Card className="grid gap-4 sm:grid-cols-2">
        <Select
          label="Class"
          value={classId}
          onChange={(event) => {
            setClassId(event.target.value);
            setSubjectId("");
          }}
        >
          <option value="">All classes</option>
          {classes?.map((klass) => (
            <option key={klass.id} value={klass.id}>
              {klass.name}
            </option>
          ))}
        </Select>
        <Select label="Subject" value={subjectId} onChange={(event) => setSubjectId(event.target.value)} disabled={!classId}>
          <option value="">All subjects</option>
          {subjects?.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.name}
            </option>
          ))}
        </Select>
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && liveClasses && liveClasses.length > 0 && (
        <div className="flex flex-col gap-3">
          {liveClasses.map((liveClass) => {
            const isPast = new Date(liveClass.scheduled_at).getTime() < now;
            return (
              <Card key={liveClass.id} className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="mb-1 flex flex-wrap items-center gap-2">
                    <Badge tone="brand">{liveClass.class_name}</Badge>
                    <Badge tone="neutral">{liveClass.subject_name}</Badge>
                    {isPast && <Badge tone="neutral">Past</Badge>}
                  </div>
                  <p className="font-medium text-slate-900">{liveClass.title}</p>
                  <p className="text-sm text-slate-500">
                    {formatDateTime(liveClass.scheduled_at)} &middot; with {liveClass.teacher_name}
                  </p>
                  {liveClass.description && (
                    <p className="mt-1 text-sm text-slate-600">{liveClass.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <a href={liveClass.meeting_url} target="_blank" rel="noopener noreferrer">
                    <Button variant="secondary">Join session</Button>
                  </a>
                  {isTeacher && (
                    <Button
                      variant="ghost"
                      className="!text-red-600"
                      onClick={() => onCancel(liveClass.id)}
                      isLoading={deleteLiveClass.isPending}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {!isLoading && liveClasses?.length === 0 && (
        <EmptyState icon="🧑‍🏫" title="No live classes scheduled" description="Check back soon, or try a different class or subject." />
      )}
    </div>
  );
}

function QuestionsSection() {
  const { data: classes } = useClasses();
  const [classId, setClassId] = useState("");
  const { data: subjects } = useSubjects(classId || undefined);
  const [subjectId, setSubjectId] = useState("");
  const { data: questions, isLoading } = useBrowseQuestions({
    classId: classId || undefined,
    subjectId: subjectId || undefined,
  });

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-display text-xl font-bold text-slate-900">Recent questions</h2>

      <Card className="grid gap-4 sm:grid-cols-2">
        <Select
          label="Class"
          value={classId}
          onChange={(event) => {
            setClassId(event.target.value);
            setSubjectId("");
          }}
        >
          <option value="">All classes</option>
          {classes?.map((klass) => (
            <option key={klass.id} value={klass.id}>
              {klass.name}
            </option>
          ))}
        </Select>
        <Select label="Subject" value={subjectId} onChange={(event) => setSubjectId(event.target.value)} disabled={!classId}>
          <option value="">All subjects</option>
          {subjects?.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.name}
            </option>
          ))}
        </Select>
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && questions && questions.length > 0 && (
        <ul className="flex flex-col divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
          {questions.map((question) => (
            <li key={question.id}>
              <Link
                to={`/lessons/${question.lesson_id}`}
                className="flex flex-col gap-1 px-5 py-4 transition-colors hover:bg-slate-50"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="neutral">{question.class_name}</Badge>
                  <Badge tone="neutral">{question.subject_name}</Badge>
                  <Badge tone={question.answer ? "success" : "warning"}>
                    {question.answer ? "Answered" : "Unanswered"}
                  </Badge>
                  {question.course_status === "DRAFT" && <Badge tone="warning">Draft</Badge>}
                </div>
                <p className="text-sm font-medium text-slate-800">{question.body}</p>
                <p className="text-xs text-slate-500">
                  {question.student_name} &middot; {question.course_title} &middot; {question.lesson_title}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {!isLoading && questions?.length === 0 && (
        <EmptyState icon="💬" title="No questions match these filters" description="Try a different class or subject." />
      )}
    </div>
  );
}

export function TeacherInteractionPage() {
  return (
    <div className="page-shell flex flex-col gap-10 py-10">
      <PageHeader
        eyebrow="Teacher Interaction"
        title="Ask questions and join live classes"
        subtitle="Ask a question right on any lesson and a teacher will answer it. Teachers can also schedule live sessions with a meeting link for real-time doubt clearing."
      />
      <LiveClassesSection />
      <QuestionsSection />
    </div>
  );
}
