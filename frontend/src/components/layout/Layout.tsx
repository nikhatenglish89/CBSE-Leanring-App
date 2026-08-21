import type { ReactNode } from "react";

import { Footer } from "./Footer";
import { Header } from "./Header";
import { VerifyEmailBanner } from "./VerifyEmailBanner";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Header />
      <VerifyEmailBanner />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
