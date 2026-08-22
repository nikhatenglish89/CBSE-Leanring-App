import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { PageHeader } from "../../components/layout/PageHeader";
import { Badge, Button, Card, CardSkeleton, EmptyState, Input, Select, useToast } from "../../components/ui";
import { useAdminUsers, useCreateUser } from "../../hooks/useAdminUsers";
import { useAuth } from "../../hooks/useAuth";
import type { AdminCreatableRole, AdminCreatedUserOut } from "../../types/users";

const ROLE_LABEL: Record<AdminCreatableRole, string> = {
  STUDENT: "Student",
  TEACHER: "Teacher",
  ADMIN: "Admin",
};

const createUserSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  full_name: z.string().min(1, "Full name is required"),
  phone: z.string().optional(),
  role: z.enum(["STUDENT", "TEACHER", "ADMIN"]),
});

type CreateUserFormValues = z.infer<typeof createUserSchema>;

function CreateUserForm({
  defaultRole,
  allowAdmin,
  onDone,
}: {
  defaultRole: AdminCreatableRole;
  allowAdmin: boolean;
  onDone: (created: AdminCreatedUserOut) => void;
}) {
  const createUser = useCreateUser();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateUserFormValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { role: defaultRole },
  });

  const onSubmit = async (values: CreateUserFormValues) => {
    try {
      const created = await createUser.mutateAsync({
        email: values.email,
        full_name: values.full_name,
        phone: values.phone || undefined,
        role: values.role,
      });
      onDone(created);
    } catch {
      showToast("Could not create the account — the email may already be in use.", "error");
    }
  };

  return (
    <Card className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-slate-900">Create account</h2>
      <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Select label="Role" {...register("role")}>
          <option value="STUDENT">Student</option>
          <option value="TEACHER">Teacher</option>
          {allowAdmin && <option value="ADMIN">Admin</option>}
        </Select>
        <Input label="Full name" error={errors.full_name?.message} {...register("full_name")} />
        <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
        <Input label="Phone (optional)" type="tel" {...register("phone")} />
        <div className="flex gap-2 sm:col-span-2">
          <Button type="submit" isLoading={createUser.isPending}>
            Create account
          </Button>
        </div>
      </form>
    </Card>
  );
}

function CreatedAccountPanel({ created, onDismiss }: { created: AdminCreatedUserOut; onDismiss: () => void }) {
  const { showToast } = useToast();

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(
        `Email: ${created.email}\nTemporary password: ${created.temporary_password}`
      );
      showToast("Credentials copied to clipboard.", "success");
    } catch {
      showToast("Could not copy — please copy manually.", "error");
    }
  };

  return (
    <Card className="flex flex-col gap-3 border-emerald-200 bg-emerald-50">
      <h2 className="text-lg font-semibold text-emerald-900">Account created</h2>
      <p className="text-sm text-emerald-800">
        Share these credentials with {created.full_name}. This password is shown only once — it can't be
        retrieved again after you leave this page.
      </p>
      <div className="rounded-lg border border-emerald-200 bg-white p-4 font-mono text-sm">
        <p>
          <span className="text-slate-500">Email:</span> {created.email}
        </p>
        <p>
          <span className="text-slate-500">Temporary password:</span> {created.temporary_password}
        </p>
      </div>
      <div className="flex gap-2">
        <Button onClick={onCopy}>Copy credentials</Button>
        <Button variant="secondary" onClick={onDismiss}>
          Done
        </Button>
      </div>
    </Card>
  );
}

export function AdminUsersPage() {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === "SUPER_ADMIN";
  const roleTabs: AdminCreatableRole[] = isSuperAdmin ? ["STUDENT", "TEACHER", "ADMIN"] : ["STUDENT", "TEACHER"];

  const [roleTab, setRoleTab] = useState<AdminCreatableRole>("STUDENT");
  const [search, setSearch] = useState("");
  const [creating, setCreating] = useState(false);
  const [createdAccount, setCreatedAccount] = useState<AdminCreatedUserOut | null>(null);
  const { data: users, isLoading } = useAdminUsers({ role: roleTab, search });

  return (
    <div className="page-shell flex flex-col gap-6 py-10">
      <PageHeader
        eyebrow="Admin"
        title={isSuperAdmin ? "Manage Students, Teachers & Admins" : "Manage Students & Teachers"}
        subtitle="Review accounts and create new ones with a temporary password — they'll be required to set their own on first login."
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
          {roleTabs.map((role) => (
            <button
              key={role}
              type="button"
              onClick={() => setRoleTab(role)}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
                roleTab === role ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {ROLE_LABEL[role]}s
            </button>
          ))}
        </div>
        {!creating && !createdAccount && (
          <Button onClick={() => setCreating(true)}>Create {ROLE_LABEL[roleTab].toLowerCase()} account</Button>
        )}
      </div>

      {createdAccount && (
        <CreatedAccountPanel created={createdAccount} onDismiss={() => setCreatedAccount(null)} />
      )}

      {creating && !createdAccount && (
        <CreateUserForm
          defaultRole={roleTab}
          allowAdmin={isSuperAdmin}
          onDone={(created) => {
            setCreating(false);
            setCreatedAccount(created);
          }}
        />
      )}

      <Card>
        <Input
          label="Search by name or email"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Start typing..."
        />
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && users && users.length > 0 && (
        <ul className="flex flex-col divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
          {users.map((u) => (
            <li key={u.id}>
              <Link
                to={`/admin/users/${u.id}`}
                className="flex flex-wrap items-center justify-between gap-2 px-5 py-4 transition-colors hover:bg-slate-50"
              >
                <div>
                  <p className="font-medium text-slate-800">{u.full_name}</p>
                  <p className="text-xs text-slate-500">{u.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  {u.must_reset_password && <Badge tone="warning">Password reset pending</Badge>}
                  <Badge tone={u.status === "ACTIVE" ? "success" : "neutral"}>{u.status}</Badge>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {!isLoading && users?.length === 0 && (
        <EmptyState
          icon="👤"
          title={`No ${ROLE_LABEL[roleTab].toLowerCase()}s found`}
          description={search ? "Try a different search." : "Create the first account above."}
        />
      )}
    </div>
  );
}
