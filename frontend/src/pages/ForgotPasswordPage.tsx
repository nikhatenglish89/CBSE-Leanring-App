import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { AuthLayout } from "../components/layout/AuthLayout";
import { Button, Input, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
});

type FormValues = z.infer<typeof schema>;

export function ForgotPasswordPage() {
  const { forgotPassword, isSendingResetLink } = useAuth();
  const { showToast } = useToast();
  const [sent, setSent] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      await forgotPassword(values.email);
      setSent(true);
    } catch {
      showToast("Something went wrong — please try again.", "error");
    }
  };

  if (sent) {
    return (
      <AuthLayout
        title="Check your email"
        subtitle="If an account exists for that address, we've sent a link to reset your password. The link expires in 1 hour."
        footer={
          <Link to="/login" className="font-medium text-brand-600 hover:underline">
            Back to log in
          </Link>
        }
      >
        <div className="flex flex-col items-center gap-3 text-center">
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-2xl">
            📬
          </span>
          <p className="text-sm text-slate-600">
            Didn't get it? Check your spam folder, or make sure you entered the same email your account uses.
          </p>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Forgot your password?"
      subtitle="Enter the email on your account and we'll send you a link to reset it."
      footer={
        <>
          Remembered it?{" "}
          <Link to="/login" className="font-medium text-brand-600 hover:underline">
            Log in
          </Link>
        </>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Button type="submit" isLoading={isSendingResetLink} className="mt-2 w-full">
          Send reset link
        </Button>
      </form>
    </AuthLayout>
  );
}
