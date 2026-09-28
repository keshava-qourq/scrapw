import { useId } from "react";
import { ArrowUpRight } from "./icons";

/** Slowly rotating circular text with an arrow in the middle. */
export default function SpinBadge({ text, className = "" }: { text: string; className?: string }) {
  const pathId = `spin-${useId().replace(/[^a-zA-Z0-9-_]/g, "")}`;
  return (
    <div aria-hidden className={`relative h-28 w-28 shrink-0 ${className}`}>
      <svg viewBox="0 0 100 100" className="h-full w-full animate-spin-slow">
        <defs>
          <path id={pathId} d="M50,50 m-38,0 a38,38 0 1,1 76,0 a38,38 0 1,1 -76,0" />
        </defs>
        <text className="fill-current font-mono text-[9px] uppercase">
          <textPath href={`#${pathId}`} textLength={236} lengthAdjust="spacing">
            {text}
          </textPath>
        </text>
      </svg>
      <span className="absolute inset-0 flex items-center justify-center">
        <ArrowUpRight className="h-6 w-6" />
      </span>
    </div>
  );
}
