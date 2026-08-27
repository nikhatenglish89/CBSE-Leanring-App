import { useEffect, useState } from "react";

import { useCaptcha } from "../../hooks/useCaptcha";
import { Input } from "./Input";
import { Spinner } from "./Spinner";

export interface CaptchaValue {
  captcha_token: string;
  captcha_answer: string;
}

interface CaptchaFieldProps {
  onChange: (value: CaptchaValue) => void;
  /** Change this to any new value (e.g. a failed-attempt counter) to force
   * a fresh challenge — the previous one has already been used/rejected. */
  reloadSignal?: unknown;
  error?: string;
}

export function CaptchaField({ onChange, reloadSignal, error }: CaptchaFieldProps) {
  const { data, isLoading, isFetching, refetch } = useCaptcha();
  const [answer, setAnswer] = useState("");

  useEffect(() => {
    onChange({ captcha_token: data?.token ?? "", captcha_answer: answer });
    // onChange is a fresh closure from the parent every render — only the
    // actual captcha state should trigger this.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.token, answer]);

  const firstRender = reloadSignal === undefined;
  useEffect(() => {
    if (firstRender) return;
    setAnswer("");
    refetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reloadSignal]);

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-slate-700">Type the code shown below</span>
      <div className="flex items-center gap-2">
        <div className="flex h-14 w-40 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-slate-300 bg-slate-100">
          {isLoading ? (
            <Spinner className="text-sm" />
          ) : (
            <div
              className="flex h-full w-full items-center justify-center [&_svg]:h-full [&_svg]:w-full"
              dangerouslySetInnerHTML={{ __html: data?.svg ?? "" }}
            />
          )}
        </div>
        <button
          type="button"
          onClick={() => {
            setAnswer("");
            refetch();
          }}
          title="Get a new code"
          aria-label="Get a new code"
          disabled={isFetching}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-300 text-lg text-slate-500 transition-colors hover:bg-slate-50 disabled:opacity-50"
        >
          ↻
        </button>
        <Input
          label=""
          aria-label="Enter the code shown above"
          placeholder="Enter the code above"
          autoComplete="off"
          value={answer}
          onChange={(event) => setAnswer(event.target.value.toUpperCase())}
          className="!py-2"
        />
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
