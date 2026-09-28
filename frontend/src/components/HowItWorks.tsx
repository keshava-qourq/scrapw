import { motion, useInView, useScroll, useTransform } from "motion/react";
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import ScrambleText from "./ui/ScrambleText";
import { EASE } from "./ui/motion";

const eyebrow = "font-mono text-[11px] uppercase tracking-[0.2em]";

function TypedQuery({ text }: { text: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.6 });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!inView || count >= text.length) return;
    const timer = window.setTimeout(() => setCount((c) => c + 1), 55);
    return () => window.clearTimeout(timer);
  }, [inView, count, text.length]);

  return (
    <span ref={ref} className="flex h-16 w-full max-w-md items-center gap-3 rounded-full border border-paper/25 px-6 text-lg">
      <span className="truncate">{text.slice(0, count)}</span>
      <span className="-ml-2 h-6 w-px animate-pulse bg-acid" />
    </span>
  );
}

function CompareBars() {
  const rows = [
    { store: "Flipkart", width: 0.64, best: true },
    { store: "Amazon", width: 0.76, best: false },
    { store: "Myntra", width: 0.88, best: false },
    { store: "AJIO", width: 1, best: false },
  ];
  return (
    <div className="w-full max-w-md space-y-4">
      {rows.map((row, i) => (
        <div key={row.store} className="grid grid-cols-[5.5rem_1fr] items-center gap-4">
          <span className="font-mono text-[11px] uppercase tracking-[0.16em]">{row.store}</span>
          <div className="h-3 overflow-hidden rounded-full bg-ink/10">
            <motion.div
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: row.width }}
              viewport={{ once: true, amount: 0.8 }}
              transition={{ duration: 1.2, ease: EASE, delay: 0.1 + i * 0.1 }}
              className={`h-full origin-left rounded-full ${row.best ? "bg-ink" : "bg-ink/35"}`}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function CardVisual() {
  return (
    <motion.div
      initial={{ rotate: 12, y: 40, opacity: 0 }}
      whileInView={{ rotate: -6, y: 0, opacity: 1 }}
      viewport={{ once: true, amount: 0.6 }}
      transition={{ duration: 1.2, ease: EASE }}
      className="relative aspect-[1.586] w-72 rounded-2xl bg-ink p-6 text-paper shadow-[0_30px_60px_-25px_rgba(13,13,12,0.6)]"
    >
      <div className="h-8 w-11 rounded-md bg-acid" />
      <p className="absolute bottom-6 left-6 font-mono text-sm tracking-[0.2em]">•••• •••• •••• 4821</p>
      <span className="absolute -right-6 -top-4 rotate-6 rounded-full bg-acid px-4 py-2 font-mono text-[11px] uppercase tracking-[0.14em] text-ink">
        Offer applied
      </span>
    </motion.div>
  );
}

const STEPS: { n: string; title: string; body: string; theme: string; visual: ReactNode }[] = [
  {
    n: "01",
    title: "Search once",
    body: "Type what you want in plain words — brands and price limits included. Every marketplace is queried at the same time.",
    theme: "bg-ink text-paper",
    visual: <TypedQuery text="Samsung 55 inch 4K TV under 50000" />,
  },
  {
    n: "02",
    title: "Compare instantly",
    body: "Duplicate listings are grouped, so the same product from different stores sits side by side, sorted your way.",
    theme: "bg-acid text-ink",
    visual: <CompareBars />,
  },
  {
    n: "03",
    title: "Pay less",
    body: "Add your bank card and its offers are applied to every result, so you see what you would actually pay.",
    theme: "bg-bone text-ink",
    visual: <CardVisual />,
  },
];

/**
 * On desktop the steps are pinned and scroll sideways as you scroll down;
 * on small screens they're a plain vertical stack.
 */
export default function HowItWorks() {
  const sectionRef = useRef<HTMLElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [distance, setDistance] = useState(0);

  useLayoutEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    const measure = () => setDistance(Math.max(0, track.scrollWidth - window.innerWidth));
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(track);
    window.addEventListener("resize", measure);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);

  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ["start start", "end end"] });
  const x = useTransform(scrollYProgress, (v) => -v * distance);
  const progress = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);

  const heading = (
    <h2 className="mt-4 text-5xl font-medium leading-[0.95] tracking-[-0.05em] lg:text-7xl">
      Three steps. <span className="font-serif font-normal italic tracking-[-0.02em]">Zero tabs.</span>
    </h2>
  );

  return (
    <>
      <section ref={sectionRef} style={{ height: `calc(100vh + ${distance}px)` }} className="relative hidden md:block">
        <div className="sticky top-0 flex h-screen flex-col justify-center gap-12 overflow-hidden">
          <div className="mx-auto flex w-full max-w-[1400px] items-end justify-between gap-8 px-8">
            <div>
              <ScrambleText text="(02) — How it works" className={`${eyebrow} text-ash`} />
              {heading}
            </div>
            <div className="mb-3 w-40 shrink-0">
              <div className="h-px bg-line">
                <motion.div style={{ width: progress }} className="h-px bg-ink" />
              </div>
            </div>
          </div>
          <motion.div
            ref={trackRef}
            style={{ x }}
            className="flex w-max gap-6 pl-8 pr-[10vw] xl:pl-[max(2rem,calc((100vw-1400px)/2+2rem))]"
          >
            {STEPS.map((step) => (
              <article
                key={step.n}
                className={`flex h-[60vh] min-h-[440px] w-[min(76vw,880px)] shrink-0 flex-col justify-between rounded-[8px] p-10 ${step.theme}`}
              >
                <div className="flex items-start justify-between gap-8">
                  <span className="font-serif text-[9rem] italic leading-[0.7]">{step.n}</span>
                  <div className="flex flex-1 justify-end pt-4">{step.visual}</div>
                </div>
                <div className="flex items-end justify-between gap-10">
                  <h3 className="text-6xl font-medium tracking-[-0.05em]">{step.title}</h3>
                  <p className="max-w-sm text-[15px] leading-relaxed opacity-70">{step.body}</p>
                </div>
              </article>
            ))}
          </motion.div>
        </div>
      </section>

      <section className="px-4 md:hidden">
        <ScrambleText text="(02) — How it works" className={`${eyebrow} text-ash`} />
        {heading}
        <div className="mt-10 space-y-4">
          {STEPS.map((step) => (
            <motion.article
              key={step.n}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "0px 0px -10% 0px" }}
              transition={{ duration: 0.9, ease: EASE }}
              className={`rounded-[8px] p-6 ${step.theme}`}
            >
              <span className="font-serif text-7xl italic leading-none">{step.n}</span>
              <h3 className="mt-6 text-4xl font-medium tracking-[-0.05em]">{step.title}</h3>
              <p className="mt-3 text-[15px] leading-relaxed opacity-70">{step.body}</p>
            </motion.article>
          ))}
        </div>
      </section>
    </>
  );
}
