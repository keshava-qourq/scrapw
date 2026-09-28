import { useId, type InputHTMLAttributes } from "react";

interface Props extends Omit<InputHTMLAttributes<HTMLInputElement>, "placeholder"> {
  label: string;
  hint?: string;
  containerClassName?: string;
}

/** Underline input whose label floats up on focus/fill and whose rule draws in from the left. */
export default function Field({ label, hint, containerClassName = "", id, ...props }: Props) {
  const autoId = useId();
  const inputId = id ?? autoId;
  return (
    <div className={containerClassName}>
      <div className="relative pt-5">
        <input
          id={inputId}
          {...props}
          placeholder=" "
          className="peer w-full border-0 border-b border-line bg-transparent pb-2.5 pt-1 text-[15px] text-ink outline-none transition-colors placeholder:text-transparent"
        />
        <label
          htmlFor={inputId}
          className="pointer-events-none absolute left-0 top-6 origin-left text-[15px] text-ash transition-all duration-500 ease-expo peer-focus:top-0 peer-focus:scale-[0.78] peer-focus:text-ink peer-[:not(:placeholder-shown)]:top-0 peer-[:not(:placeholder-shown)]:scale-[0.78]"
        >
          {label}
        </label>
        <span
          aria-hidden
          className="absolute bottom-0 left-0 h-px w-full origin-left scale-x-0 bg-ink transition-transform duration-700 ease-expo peer-focus:scale-x-100"
        />
      </div>
      {hint && <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.16em] text-ash">{hint}</p>}
    </div>
  );
}
