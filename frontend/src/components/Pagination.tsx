import { ArrowRight } from "./ui/icons";
import Magnetic from "./ui/Magnetic";

interface Props {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number) => void;
}

const pad = (n: number) => String(n).padStart(2, "0");

const BUTTON =
  "flex h-14 w-14 items-center justify-center rounded-full border border-ink transition-colors duration-300 hover:bg-ink hover:text-paper disabled:pointer-events-none disabled:opacity-20";

export default function Pagination({ page, pageSize, total, onChange }: Props) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if (totalPages <= 1) return null;

  return (
    <nav aria-label="Pagination" className="mt-24 flex items-center justify-between border-t border-ink pt-6">
      <Magnetic>
        <button onClick={() => onChange(page - 1)} disabled={page <= 1} aria-label="Previous page" className={BUTTON}>
          <ArrowRight className="h-5 w-5 rotate-180" />
        </button>
      </Magnetic>
      <p className="font-mono text-sm tracking-[0.2em] tabular-nums">
        {pad(page)} <span className="text-ash">/ {pad(totalPages)}</span>
      </p>
      <Magnetic>
        <button onClick={() => onChange(page + 1)} disabled={page >= totalPages} aria-label="Next page" className={BUTTON}>
          <ArrowRight className="h-5 w-5" />
        </button>
      </Magnetic>
    </nav>
  );
}
