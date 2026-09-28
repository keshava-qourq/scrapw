interface Props {
  children: string;
  /** Extra classes for the copy that rolls in, e.g. to swap it to the serif italic. */
  hoverClassName?: string;
  className?: string;
}

/** Label that rolls up and is replaced by a copy of itself when a `group` ancestor is hovered. */
export default function RollText({ children, hoverClassName = "", className = "" }: Props) {
  return (
    <span className={`relative inline-flex overflow-hidden ${className}`}>
      <span className="transition-transform duration-500 ease-expo group-hover:-translate-y-full">{children}</span>
      <span
        aria-hidden
        className={`absolute inset-0 translate-y-full transition-transform duration-500 ease-expo group-hover:translate-y-0 ${hoverClassName}`}
      >
        {children}
      </span>
    </span>
  );
}
