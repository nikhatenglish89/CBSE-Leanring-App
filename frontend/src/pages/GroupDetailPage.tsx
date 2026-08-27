import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useParams } from "react-router-dom";
import { z } from "zod";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Spinner, Textarea, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { useAddGroupMember, useCreateGroupTask, useGroupDetail, useRemoveGroupMember } from "../hooks/useGroups";
import { useMessageableUsers } from "../hooks/useMessaging";
import { formatDateTime } from "../lib/format";

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
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
