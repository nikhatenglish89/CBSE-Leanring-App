import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { AuthLayout } from "../components/layout/AuthLayout";
import { Button, Input, useToast } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { roleHomePath } from "../lib/roleRoutes";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { login, isLoggingIn } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      const user = await login(values);
      navigate(roleHomePath(user.role));
    } catch {
      showToast("Incorrect email or password.", "error");
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to continue where you left off."
      footer={
        <>
          Don't have an account?{" "}
          <Link to="/register" className="font-medium text-brand-600 hover:underline">
            Register
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
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Link to="/forgot-password" className="-mt-2 self-end text-sm font-medium text-brand-600 hover:underline">
          Forgot password?
        </Link>
        <Button type="submit" isLoading={isLoggingIn} className="mt-2 w-full">
          Log in
        </Button>
      </form>
    </AuthLayout>
  );
}
