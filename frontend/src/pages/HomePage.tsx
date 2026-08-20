import { Link } from "react-router-dom";

import { Button, Card } from "../components/ui";
import { BRAND } from "../config/brand";

export function HomePage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col items-center gap-6 px-4 py-24 text-center">
      <h1 className="text-4xl font-bold tracking-tight text-slate-900">{BRAND.tagline}</h1>
      <p className="max-w-xl text-slate-600">
        {BRAND.name} is a CBSE-focused learning platform for classes 6&ndash;12 &mdash; video
        lessons, study material, live classes, tests, and more.
      </p>
      <Card className="flex w-full max-w-sm flex-col gap-3">
        <Link to="/register">
          <Button className="w-full">Start Learning</Button>
        </Link>
        <Link to="/login">
          <Button variant="secondary" className="w-full">
            I already have an account
          </Button>
        </Link>
      </Card>
    </div>
  );
}
