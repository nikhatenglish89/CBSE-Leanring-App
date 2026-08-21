import { useState } from "react";

import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../ui";

export function VerifyEmailBanner() {
  const { user, isAuthenticated, resendVerification, isResendingVerification } = useAuth();
  const { showToast } = useToast();
  const [sent, setSent] = useState(false);

  if (!isAuthenticated || !user || user.email_verified) return null;

  const onResend = async () => {
    try {
      await resendVerification();
      setSent(true);
      showToast("Verification email sent — check your inbox.", "success");
    } catch {
      showToast("Could not send the verification email. Try again shortly.", "error");
    }
  };

  return (
    <div className="border-b border-amber-200 bg-amber-50">
      <div className="page-shell flex flex-wrap items-center justify-center gap-2 py-2.5 text-center text-sm text-amber-800 sm:justify-between">
        <p>
          <span className="font-medium">Please verify your email</span> ({user.email}) to secure your
          account.
        </p>
        <button
          type="button"
          onClick={onResend}
          disabled={isResendingVerification || sent}
          className="font-medium text-amber-900 underline decoration-amber-400 underline-offset-2 hover:decoration-amber-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {sent ? "Sent — check your inbox" : isResendingVerification ? "Sending…" : "Resend email"}
        </button>
      </div>
    </div>
  );
}
