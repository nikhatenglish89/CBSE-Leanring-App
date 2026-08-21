import { Link } from "react-router-dom";

import { Badge, Button, Card } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { roleHomePath } from "../lib/roleRoutes";

export function ComingSoonPage({
  icon,
  eyebrow,
  title,
  description,
  highlights,
}: {
  icon: string;
  eyebrow: string;
  title: string;
  description: string;
  highlights: string[];
}) {
  const { user, isAuthenticated } = useAuth();

  return (
    <div className="page-shell flex flex-col items-center py-16 text-center">
      <Card className="max-w-xl">
        <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-3xl">
          {icon}
        </span>
        <Badge tone="warning" className="mx-auto mt-4 w-fit gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" /> Coming soon
        </Badge>
        <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-brand-600">{eyebrow}</p>
        <h1 className="mt-1 font-display text-2xl font-bold text-slate-900 sm:text-3xl">{title}</h1>
        <p className="mt-3 text-slate-600">{description}</p>

        <ul className="mt-6 flex flex-col gap-2 text-left">
          {highlights.map((item) => (
            <li key={item} className="flex items-start gap-2 text-sm text-slate-700">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs text-brand-600">
                ✓
              </span>
              {item}
            </li>
          ))}
        </ul>

        <div className="mt-8">
          <Link to={isAuthenticated && user ? roleHomePath(user.role) : "/register"}>
            <Button>{isAuthenticated ? "Back to your dashboard" : "Create a free account"}</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
