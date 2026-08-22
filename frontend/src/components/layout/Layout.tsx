import type { ReactNode } from "react";

import { useAuth } from "../../hooks/useAuth";
import { ChatWidget } from "../assistant/ChatWidget";
import { Footer } from "./Footer";
import { Header } from "./Header";
import { VerifyEmailBanner } from "./VerifyEmailBanner";

export function Layout({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Header />
      <VerifyEmailBanner />
      <main className="flex-1">{children}</main>
      <Footer />
      {isAuthenticated && <ChatWidget />}
    </div>
  );
}
