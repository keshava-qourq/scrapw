export default function Wordmark({ inverted = false }: { inverted?: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-2 text-[19px] font-semibold tracking-[-0.04em] ${inverted ? "text-paper" : "text-ink"}`}
    >
      <span className="flex h-6 w-6 items-center justify-center rounded-[6px] bg-acid">
        <span className="h-2 w-2 rounded-full bg-ink" />
      </span>
      <span>
        scrap<span className="font-serif text-[23px] font-normal italic">w</span>
      </span>
    </span>
  );
}
