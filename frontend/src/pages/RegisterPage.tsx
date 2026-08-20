import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { Button, Card, Input, useToast } from "../components/ui";
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
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { role: "STUDENT" } });

  const onSubmit = async (values: FormValues) => {
    try {
      const user = await registerUser(values);
      navigate(roleHomePath(user.role));
    } catch {
      showToast("Could not create your account. The email may already be registered.", "error");
    }
  };

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-4 py-16">
      <h1 className="text-2xl font-semibold text-slate-900">Create your account</h1>
      <Card>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
          <Input label="Full name" error={errors.full_name?.message} {...register("full_name")} />
          <Input label="Email" type="email" autoComplete="email" error={errors.email?.message} {...register("email")} />
          <Input
            label="Password"
            type="password"
            autoComplete="new-password"
            error={errors.password?.message}
            {...register("password")}
          />
          <div className="flex flex-col gap-1">
            <label htmlFor="role" className="text-sm font-medium text-slate-700">
              I am a
            </label>
            <select
              id="role"
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100"
              {...register("role")}
            >
              <option value="STUDENT">Student</option>
              <option value="PARENT">Parent</option>
              <option value="TEACHER">Teacher</option>
            </select>
          </div>
          <Button type="submit" isLoading={isRegistering}>
            Create account
          </Button>
        </form>
      </Card>
      <p className="text-center text-sm text-slate-600">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
