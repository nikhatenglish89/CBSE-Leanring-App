import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { PageHeader } from "../components/layout/PageHeader";
import { Badge, Button, Card, Input, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";

const ROLE_LABEL: Record<string, string> = {
  STUDENT: "Student",
  TEACHER: "Teacher",
  PARENT: "Parent",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
  CONTENT_MANAGER: "Content Manager",
  SUPPORT_AGENT: "Support Agent",
};

const schema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  phone: z
    .string()
    .trim()
    .regex(/^\+?[0-9()\-\s]{7,20}$/, "Enter a valid phone number")
    .or(z.literal(""))
    .optional(),
});

type FormValues = z.infer<typeof schema>;

const passwordSchema = z
  .object({
    current_password: z.string().min(1, "Current password is required"),
    new_password: z.string().min(8, "New password must be at least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your new password"),
  })
  .refine((values) => values.new_password === values.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type PasswordFormValues = z.infer<typeof passwordSchema>;

export function ProfilePage() {
  const { user, updateProfile, isUpdatingProfile, changePassword, isChangingPassword } = useAuth();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { full_name: user?.full_name ?? "", phone: user?.phone ?? "" },
  });

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    reset: resetPasswordForm,
    formState: { errors: passwordErrors },
  } = useForm<PasswordFormValues>({ resolver: zodResolver(passwordSchema) });

  useEffect(() => {
    reset({ full_name: user?.full_name ?? "", phone: user?.phone ?? "" });
  }, [user, reset]);

  const onSubmit = async (values: FormValues) => {
    try {
      const updated = await updateProfile({
        full_name: values.full_name,
        phone: values.phone ? values.phone : null,
      });
      reset({ full_name: updated.full_name, phone: updated.phone ?? "" });
      showToast("Your profile has been updated.", "success");
    } catch {
      showToast("Could not update your profile. Please try again.", "error");
    }
  };

  const onChangePassword = async (values: PasswordFormValues) => {
    try {
      await changePassword({
        current_password: values.current_password,
        new_password: values.new_password,
      });
      resetPasswordForm();
      showToast("Your password has been changed.", "success");
    } catch {
      showToast("Could not change your password — check your current password and try again.", "error");
    }
  };

  if (!user) return null;

  return (
    <div className="page-shell flex flex-col gap-8 py-10 sm:py-14">
      <PageHeader eyebrow="Account" title="Edit profile" subtitle="Keep your contact details up to date." />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <div className="flex flex-col items-center gap-3 text-center">
            <span className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-xl font-semibold text-brand-700">
              {user.full_name
                .trim()
                .split(/\s+/)
                .map((part) => part[0])
                .slice(0, 2)
                .join("")
                .toUpperCase()}
            </span>
            <div>
              <p className="font-semibold text-slate-900">{user.full_name}</p>
              <p className="text-sm text-slate-500">{user.email}</p>
            </div>
            <Badge tone="brand">{ROLE_LABEL[user.role] ?? user.role}</Badge>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input
              label="Full name"
              error={errors.full_name?.message}
              {...register("full_name")}
            />
            <Input
              label="Phone number"
              type="tel"
              placeholder="e.g. +91 98765 43210"
              error={errors.phone?.message}
              {...register("phone")}
            />
            <Input label="Email address" value={user.email} disabled readOnly />
            <p className="-mt-2 text-xs text-slate-500">
              Your email is your login ID and can&rsquo;t be changed here.
            </p>
            <div className="flex justify-end">
              <Button type="submit" isLoading={isUpdatingProfile} disabled={!isDirty}>
                Save changes
              </Button>
            </div>
          </form>
        </Card>

        <Card className="lg:col-span-2 lg:col-start-2">
          <h2 className="mb-1 text-lg font-semibold text-slate-900">Change password</h2>
          <p className="mb-4 text-sm text-slate-500">
            Changing your password will sign you out of your other devices.
          </p>
          <form
            className="flex flex-col gap-4"
            onSubmit={handlePasswordSubmit(onChangePassword)}
            noValidate
          >
            <Input
              label="Current password"
              type="password"
              autoComplete="current-password"
              error={passwordErrors.current_password?.message}
              {...registerPassword("current_password")}
            />
            <Input
              label="New password"
              type="password"
              autoComplete="new-password"
              error={passwordErrors.new_password?.message}
              {...registerPassword("new_password")}
            />
            <Input
              label="Confirm new password"
              type="password"
              autoComplete="new-password"
              error={passwordErrors.confirm_password?.message}
              {...registerPassword("confirm_password")}
            />
            <div className="flex justify-end">
              <Button type="submit" isLoading={isChangingPassword}>
                Update password
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
