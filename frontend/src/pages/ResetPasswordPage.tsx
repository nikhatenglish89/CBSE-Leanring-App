import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { z } from "zod";

import { AuthLayout } from "../components/layout/AuthLayout";
import { Button, Input, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";

const schema = z
  .object({
    new_password: z.string().min(8, "New password must be at least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your new password"),
  })
  .refine((values) => values.new_password === values.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type FormValues = z.infer<typeof schema>;

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const { resetPassword, isResettingPassword } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [linkInvalid, setLinkInvalid] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    if (!token) return;
    try {
      await resetPassword({ token, new_password: values.new_password });
      showToast("Password updated. Please log in with your new password.", "success");
      navigate("/login", { replace: true });
    } catch (error) {
      // The link is only discovered to be invalid/expired at submit time —
      // there's no way to check it up front without spending it.
      const code = axios.isAxiosError(error) ? error.response?.data?.error?.code : undefined;
      if (code === "INVALID_TOKEN") {
        setLinkInvalid(true);
      } else {
        showToast("Could not reset your password — please try again.", "error");
      }
    }
  };

  if (!token || linkInvalid) {
    return (
      <AuthLayout
        title="This link is invalid or expired"
        subtitle="Password reset links expire after 1 hour. Request a new one to continue."
        footer={<span className="text-slate-500">Only the most recent reset link for your account works.</span>}
      >
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-2xl">
            ⚠️
          </span>
          <Link to="/forgot-password">
            <Button>Request a new link</Button>
          </Link>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Choose a new password"
      subtitle="Enter a new password for your account."
      footer={
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          Back to log in
        </Link>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
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
        <Button type="submit" isLoading={isResettingPassword} className="mt-2 w-full">
          Reset password
        </Button>
      </form>
    </AuthLayout>
  );
}
