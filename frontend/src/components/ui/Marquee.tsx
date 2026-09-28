import type { CSSProperties, ReactNode } from "react";

interface Props {
  items: ReactNode[];
  duration?: number;
  reverse?: boolean;
  className?: string;
}

/** Endless horizontal ticker: two identical rows, translated by half their combined width. */
export default function Marquee({ items, duration = 32, reverse = false, className = "" }: Props) {
  const row = (hidden: boolean) => (
    <div aria-hidden={hidden || undefined} className="flex shrink-0 items-center">
      {[...items, ...items, ...items].map((item, i) => (
        <span key={i} className="flex shrink-0 items-center">
          {item}
        </span>
      ))}
    </div>
  );

  return (
    <div className={`overflow-hidden ${className}`}>
      <div
        className={`flex w-max animate-marquee hover:[animation-play-state:paused] ${reverse ? "[animation-direction:reverse]" : ""}`}
        style={{ "--marquee-duration": `${duration}s` } as CSSProperties}
      >
        {row(false)}
        {row(true)}
      </div>
    </div>
  );
}
