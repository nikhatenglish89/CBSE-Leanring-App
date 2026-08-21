import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Button, Card, Spinner } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";
import { roleHomePath } from "../lib/roleRoutes";

type Status = "verifying" | "success" | "error";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<Status>("verifying");
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!token) {
      setStatus("error");
      return;
    }
    api
      .post("/auth/verify-email", { token })
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [token]);

  return (
    <div className="page-shell flex flex-col items-center py-16 text-center">
      <Card className="max-w-md">
        {status === "verifying" && (
          <>
            <Spinner className="mx-auto" />
            <h1 className="mt-4 font-display text-xl font-bold text-slate-900">Verifying your email&hellip;</h1>
          </>
        )}

        {status === "success" && (
          <>
            <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-2xl">
              ✅
            </span>
            <h1 className="mt-4 font-display text-xl font-bold text-slate-900">Email verified</h1>
            <p className="mt-2 text-slate-600">Your email address has been confirmed. You're all set.</p>
            <Link
              to={isAuthenticated && user ? roleHomePath(user.role) : "/login"}
              className="mt-6 inline-block"
            >
              <Button>{isAuthenticated ? "Go to your dashboard" : "Log in"}</Button>
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-2xl">
              ⚠️
            </span>
            <h1 className="mt-4 font-display text-xl font-bold text-slate-900">
              This link is invalid or expired
            </h1>
            <p className="mt-2 text-slate-600">
              Verification links expire after 24 hours. Log in and use the "Resend" option to get a
              new one.
            </p>
            <Link to="/login" className="mt-6 inline-block">
              <Button>Log in</Button>
            </Link>
          </>
        )}
      </Card>
    </div>
  );
}
