import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { AuthLayout } from "../components/layout/AuthLayout";
import { Button, CaptchaField, Input, Select, useToast } from "../components/ui";
import type { CaptchaValue } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { roleHomePath } from "../lib/roleRoutes";

const schema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  role: z.enum(["STUDENT", "PARENT", "TEACHER"]),
});

type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
  const { register: registerUser, isRegistering } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [captcha, setCaptcha] = useState<CaptchaValue>({ captcha_token: "", captcha_answer: "" });
  const [captchaAttempt, setCaptchaAttempt] = useState(0);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { role: "STUDENT" } });

  const onSubmit = async (values: FormValues) => {
    try {
      const user = await registerUser({ ...values, ...captcha });
      showToast("Account created! Check your email to verify your address.", "success");
      navigate(roleHomePath(user.role));
    } catch (error) {
      const apiError = axios.isAxiosError(error) ? error.response?.data?.error : undefined;
      setCaptchaAttempt((n) => n + 1);
      showToast(
        apiError?.code === "CAPTCHA_INVALID"
          ? "That code didn't match — please try the new one below."
          : "Could not create your account. The email may already be registered.",
        "error"
      );
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Join as a student, teacher, or parent — free."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-600 hover:underline">
            Log in
          </Link>
        </>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Input label="Full name" error={errors.full_name?.message} {...register("full_name")} />
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Select label="I am a" {...register("role")}>
          <option value="STUDENT">Student</option>
          <option value="PARENT">Parent</option>
          <option value="TEACHER">Teacher</option>
        </Select>
        <CaptchaField onChange={setCaptcha} reloadSignal={captchaAttempt || undefined} />
        <Button type="submit" isLoading={isRegistering} className="mt-2 w-full">
          Create account
        </Button>
      </form>
    </AuthLayout>
  );
}
