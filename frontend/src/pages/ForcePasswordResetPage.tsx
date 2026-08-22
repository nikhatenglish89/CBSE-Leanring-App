import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { AuthLayout } from "../components/layout/AuthLayout";
import { Button, Input, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { roleHomePath } from "../lib/roleRoutes";
import { useAuthStore } from "../store/authStore";

const schema = z
  .object({
    current_password: z.string().min(1, "Enter the temporary password you were given"),
    new_password: z.string().min(8, "New password must be at least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your new password"),
  })
  .refine((values) => values.new_password === values.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type FormValues = z.infer<typeof schema>;

export function ForcePasswordResetPage() {
  const { user, changePassword, isChangingPassword } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      await changePassword({ current_password: values.current_password, new_password: values.new_password });
      if (user) useAuthStore.getState().updateUser({ ...user, must_reset_password: false });
      showToast("Password updated. Welcome to EduSphere!", "success");
      navigate(roleHomePath(user?.role ?? "STUDENT"), { replace: true });
    } catch {
      showToast("Could not update your password — check the temporary password and try again.", "error");
    }
  };

  return (
    <AuthLayout
      title="Set a new password"
      subtitle="Your account was created by an admin with a temporary password. Set your own password to continue."
      footer={<span className="text-slate-500">You can't access EduSphere until this is done.</span>}
    >
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Input
          label="Temporary password"
          type="password"
          autoComplete="current-password"
          error={errors.current_password?.message}
          {...register("current_password")}
        />
        <Input
          label="New password"
          type="password"
          autoComplete="new-password"
          error={errors.new_password?.message}
          {...register("new_password")}
        />
        <Input
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          error={errors.confirm_password?.message}
          {...register("confirm_password")}
        />
        <Button type="submit" isLoading={isChangingPassword} className="mt-2 w-full">
          Set password &amp; continue
        </Button>
      </form>
    </AuthLayout>
  );
}
