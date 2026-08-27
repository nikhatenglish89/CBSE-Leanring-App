import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { PageHeader } from "../components/layout/PageHeader";
import { Button, Card, CardSkeleton, EmptyState, Textarea, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { useCreateGroup, useMyGroups } from "../hooks/useGroups";
import { formatDateTime } from "../lib/format";

const schema = z.object({
  name: z.string().min(1, "Give the group a name").max(150),
  description: z.string().max(2000).optional(),
});

type FormValues = z.infer<typeof schema>;

export function GroupsPage() {
  const { user } = useAuth();
  const isTeacher = user?.role === "TEACHER";
  const { data: groups, isLoading } = useMyGroups();
  const createGroup = useCreateGroup();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      const group = await createGroup.mutateAsync(values);
      reset();
      showToast(`Group "${group.name}" created — add students to it below.`, "success");
    } catch (error) {
      const message = axios.isAxiosError(error) ? error.response?.data?.error?.message : undefined;
      showToast(message ?? "Could not create the group.", "error");
    }
  };

  return (
    <div className="page-shell flex flex-col gap-8 py-10">
      <PageHeader
        eyebrow="Groups"
        title={isTeacher ? "Your student groups" : "Your groups"}
        subtitle={
          isTeacher
            ? "Create a group of students and assign shared tasks to all of them at once."
            : "Groups your teachers have added you to, with any tasks they've assigned."
        }
      />

      {isTeacher && (
        <Card className="flex flex-col gap-4">
          <h2 className="text-lg font-semibold text-slate-900">Create a group</h2>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Group name</label>
              <input
                placeholder="e.g. Physics Toppers"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100"
                {...register("name")}
              />
              {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
            </div>
            <Textarea label="Description (optional)" rows={2} {...register("description")} />
            <Button type="submit" isLoading={createGroup.isPending} className="self-start">
              Create group
            </Button>
          </form>
        </Card>
      )}

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">{isTeacher ? "Your groups" : "Groups you're in"}</h2>
        {isLoading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        )}
        {!isLoading && groups && groups.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {groups.map((group) => (
              <Link key={group.id} to={`/groups/${group.id}`}>
                <Card className="flex h-full flex-col gap-2 transition-shadow hover:shadow-lg">
                  <h3 className="font-semibold text-slate-900">{group.name}</h3>
                  {group.description && <p className="line-clamp-2 text-sm text-slate-500">{group.description}</p>}
                  <div className="mt-auto flex items-center gap-4 pt-2 text-xs text-slate-500">
                    <span>{group.member_count} student{group.member_count === 1 ? "" : "s"}</span>
                    <span>{group.task_count} task{group.task_count === 1 ? "" : "s"}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">Created {formatDateTime(group.created_at)}</p>
                </Card>
              </Link>
            ))}
          </div>
        )}
        {!isLoading && groups?.length === 0 && (
          <EmptyState
            icon="👥"
            title="No groups yet"
            description={isTeacher ? "Create your first group above to get started." : "You haven't been added to a group yet."}
          />
        )}
      </div>
    </div>
  );
}
