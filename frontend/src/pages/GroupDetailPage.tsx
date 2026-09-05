import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { type FormEvent, useState } from "react";
import { useForm } from "react-hook-form";
import { useParams } from "react-router-dom";
import { z } from "zod";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Spinner, Textarea, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import {
  downloadSubmissionFile,
  useAddGroupMember,
  useCreateGroupTask,
  useGroupDetail,
  useRemoveGroupMember,
  useSubmitTask,
  useTaskSubmissions,
} from "../hooks/useGroups";
import { useMessageableUsers } from "../hooks/useMessaging";
import { formatDateTime, formatFileSize } from "../lib/format";
import type { GroupTask } from "../types/groups";

const taskSchema = z.object({
  title: z.string().min(1, "Give the task a title").max(200),
  description: z.string().max(4000).optional(),
  due_date: z.string().optional(),
});

type TaskFormValues = z.infer<typeof taskSchema>;

function AddStudentPanel({ groupId, memberIds }: { groupId: string; memberIds: string[] }) {
  const [search, setSearch] = useState("");
  const { data: candidates, isLoading } = useMessageableUsers(search);
  const addMember = useAddGroupMember(groupId);
  const { showToast } = useToast();

  const available = candidates?.filter((c) => !memberIds.includes(c.id)) ?? [];

  const onPick = async (studentId: string) => {
    try {
      await addMember.mutateAsync(studentId);
      showToast("Student added to the group.", "success");
    } catch (error) {
      const message = axios.isAxiosError(error) ? error.response?.data?.error?.message : undefined;
      showToast(message ?? "Could not add that student.", "error");
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <input
        placeholder="Search students by name..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
      />
      <div className="flex max-h-48 flex-col gap-1 overflow-y-auto">
        {isLoading && <Spinner className="mx-auto my-2" />}
        {!isLoading && available.length === 0 && (
          <p className="py-2 text-center text-sm text-slate-500">No students found.</p>
        )}
        {available.map((student) => (
          <button
            key={student.id}
            type="button"
            onClick={() => onPick(student.id)}
            disabled={addMember.isPending}
            className="flex items-center justify-between rounded-lg px-2 py-2 text-left text-sm hover:bg-slate-50 disabled:opacity-50"
          >
            {student.full_name}
            <span className="text-xs text-brand-600">Add</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function TaskSubmissionForm({ groupId, task }: { groupId: string; task: GroupTask }) {
  const submitTask = useSubmitTask(groupId, task.id);
  const { showToast } = useToast();
  const [content, setContent] = useState(task.my_submission?.content ?? "");
  const [file, setFile] = useState<File | null>(null);
  const [isEditing, setIsEditing] = useState(!task.my_submission);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmed = content.trim();
    if (!trimmed && !file) return;
    try {
      await submitTask.mutateAsync({ content: trimmed, file });
      setFile(null);
      setIsEditing(false);
      showToast(task.my_submission ? "Submission updated." : "Task submitted.", "success");
    } catch {
      showToast("Could not submit your work.", "error");
    }
  };

  if (!isEditing && task.my_submission) {
    const submission = task.my_submission;
    return (
      <div className="mt-2 flex flex-col gap-2 rounded-lg bg-emerald-50 p-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <Badge tone="success">Submitted {formatDateTime(submission.updated_at)}</Badge>
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            className="text-xs font-medium text-brand-600 hover:underline"
          >
            Edit submission
          </button>
        </div>
        {submission.content && (
          <p className="whitespace-pre-wrap text-sm text-slate-700">{submission.content}</p>
        )}
        {submission.file_name && (
          <button
            type="button"
            onClick={() =>
              downloadSubmissionFile(groupId, task.id, submission.id, submission.file_name as string)
            }
            className="flex w-fit items-center gap-2 rounded-lg border border-emerald-200 bg-white px-3 py-1.5 text-xs font-medium text-brand-600 hover:underline"
          >
            📎 {submission.file_name}
            {submission.file_size != null && (
              <span className="text-slate-400">({formatFileSize(submission.file_size)})</span>
            )}
          </button>
        )}
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="mt-2 flex flex-col gap-2">
      <textarea
        value={content}
        onChange={(event) => setContent(event.target.value)}
        rows={3}
        placeholder="Type your answer or notes here..."
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
      />
      <input
        type="file"
        accept=".pdf,.doc,.docx,.txt,image/png,image/jpeg,image/webp"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        className="text-xs text-slate-500 file:mr-3 file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-slate-700 hover:file:bg-slate-200"
      />
      {!file && task.my_submission?.file_name && (
        <p className="text-xs text-slate-500">
          Keeping current attachment: {task.my_submission.file_name}
        </p>
      )}
      <div className="flex items-center gap-3">
        <Button
          type="submit"
          isLoading={submitTask.isPending}
          disabled={!content.trim() && !file}
          className="self-start"
        >
          {task.my_submission ? "Update submission" : "Submit"}
        </Button>
        {task.my_submission && (
          <button
            type="button"
            onClick={() => {
              setContent(task.my_submission?.content ?? "");
              setFile(null);
              setIsEditing(false);
            }}
            className="text-sm text-slate-500 hover:text-slate-700"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

function TaskSubmissionsPanel({ groupId, task }: { groupId: string; task: GroupTask }) {
  const [show, setShow] = useState(false);
  const { data: submissions, isLoading } = useTaskSubmissions(groupId, show ? task.id : null);

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => setShow((v) => !v)}
        className="text-xs font-medium text-brand-600 hover:underline"
      >
        {show ? "Hide submissions" : `View submissions (${task.submission_count})`}
      </button>
      {show && (
        <div className="mt-2 flex flex-col gap-2">
          {isLoading && <Spinner className="mx-auto my-2" />}
          {!isLoading && submissions?.length === 0 && (
            <p className="text-sm text-slate-500">No submissions yet.</p>
          )}
          {submissions?.map((submission) => (
            <div key={submission.id} className="rounded-lg border border-slate-200 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-medium text-slate-800">{submission.student_name}</p>
                <span className="text-xs text-slate-400">{formatDateTime(submission.updated_at)}</span>
              </div>
              {submission.content && (
                <p className="mt-1 whitespace-pre-wrap text-sm text-slate-600">{submission.content}</p>
              )}
              {submission.file_name && (
                <button
                  type="button"
                  onClick={() =>
                    downloadSubmissionFile(groupId, task.id, submission.id, submission.file_name as string)
                  }
                  className="mt-2 flex w-fit items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-brand-600 hover:underline"
                >
                  📎 {submission.file_name}
                  {submission.file_size != null && (
                    <span className="text-slate-400">({formatFileSize(submission.file_size)})</span>
                  )}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function GroupDetailPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: group, isLoading } = useGroupDetail(groupId);
  const removeMember = useRemoveGroupMember(groupId ?? "");
  const createTask = useCreateGroupTask(groupId ?? "");
  const { showToast } = useToast();
  const [showAddStudent, setShowAddStudent] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TaskFormValues>({ resolver: zodResolver(taskSchema) });

  const isOwner = Boolean(group && user && group.teacher_id === user.id);

  const onRemove = async (studentId: string) => {
    try {
      await removeMember.mutateAsync(studentId);
    } catch {
      showToast("Could not remove that student.", "error");
    }
  };

  const onCreateTask = async (values: TaskFormValues) => {
    try {
      await createTask.mutateAsync({
        title: values.title,
        description: values.description,
        due_date: values.due_date ? new Date(values.due_date).toISOString() : null,
      });
      reset();
      showToast("Task assigned to the group.", "success");
    } catch {
      showToast("Could not assign the task.", "error");
    }
  };

  if (isLoading || !group) {
    return (
      <div className="page-shell flex flex-col gap-4 py-10">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Group"
        title={group.name}
        subtitle={group.description || `Taught by ${group.teacher_name}`}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Students ({group.members.length})</h2>
            {isOwner && (
              <Button variant="secondary" onClick={() => setShowAddStudent((v) => !v)}>
                Add student
              </Button>
            )}
          </div>

          {isOwner && showAddStudent && <AddStudentPanel groupId={group.id} memberIds={group.members.map((m) => m.id)} />}

          {group.members.length === 0 ? (
            <EmptyState icon="👥" title="No students yet" description={isOwner ? "Add students to this group above." : ""} />
          ) : (
            <ul className="flex flex-col divide-y divide-slate-100">
              {group.members.map((member) => (
                <li key={member.id} className="flex items-center justify-between py-2.5">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{member.full_name}</p>
                    <p className="text-xs text-slate-500">{member.email}</p>
                  </div>
                  {isOwner && (
                    <button
                      type="button"
                      onClick={() => onRemove(member.id)}
                      className="text-xs font-medium text-red-600 hover:text-red-700"
                    >
                      Remove
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="text-lg font-semibold text-slate-900">Tasks ({group.tasks.length})</h2>

          {isOwner && (
            <form className="flex flex-col gap-3 rounded-lg border border-slate-200 p-3" onSubmit={handleSubmit(onCreateTask)} noValidate>
              <div>
                <input
                  placeholder="Task title"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
                  {...register("title")}
                />
                {errors.title && <p className="mt-1 text-xs text-red-600">{errors.title.message}</p>}
              </div>
              <Textarea label="Details (optional)" rows={2} {...register("description")} />
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Due date (optional)</label>
                <input
                  type="date"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
                  {...register("due_date")}
                />
              </div>
              <Button type="submit" isLoading={createTask.isPending} className="self-start">
                Assign task
              </Button>
            </form>
          )}

          {group.tasks.length === 0 ? (
            <EmptyState icon="📋" title="No tasks yet" description={isOwner ? "Assign a task to the group above." : "Nothing assigned yet."} />
          ) : (
            <ul className="flex flex-col divide-y divide-slate-100">
              {group.tasks.map((task) => (
                <li key={task.id} className="flex flex-col gap-1 py-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-medium text-slate-900">{task.title}</p>
                    {task.due_date && <Badge tone="warning">Due {formatDateTime(task.due_date)}</Badge>}
                  </div>
                  {task.description && <p className="whitespace-pre-wrap text-sm text-slate-600">{task.description}</p>}
                  {isOwner ? (
                    <TaskSubmissionsPanel groupId={group.id} task={task} />
                  ) : (
                    <TaskSubmissionForm groupId={group.id} task={task} />
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
