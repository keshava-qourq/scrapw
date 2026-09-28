import { AnimatePresence, motion, useAnimate } from "motion/react";
import { useState, type FormEvent } from "react";
import { login, register } from "../api";
import type { User } from "../types";
import Field from "./ui/Field";
import { ArrowRight } from "./ui/icons";
import Marquee from "./ui/Marquee";
import RevealText from "./ui/RevealText";
import RollText from "./ui/RollText";
import SpinBadge from "./ui/SpinBadge";
import Wordmark from "./ui/Wordmark";
import { EASE, useCycle } from "./ui/motion";

interface LoginViewProps {
  onAuthenticated: (user: User) => void;
}

const CYCLING_WORDS = ["smarter.", "cheaper.", "everywhere.", "once."];
const MARKETPLACES = ["Amazon", "Flipkart", "Myntra", "AJIO"];

export default function LoginView({ onAuthenticated }: LoginViewProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formScope, animateForm] = useAnimate<HTMLFormElement>();
  const wordIndex = useCycle(CYCLING_WORDS.length, 2400);

  const isRegister = mode === "register";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const user = isRegister ? await register(email, password) : await login(email, password);
      onAuthenticated(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      animateForm(formScope.current, { x: [0, -12, 10, -6, 4, 0] }, { duration: 0.5 });
    } finally {
      setSubmitting(false);
    }
  }

  function switchMode() {
    setMode(isRegister ? "login" : "register");
    setError(null);
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.15fr_1fr]">
      <motion.aside
        initial={{ clipPath: "inset(0 100% 0 0)" }}
        animate={{ clipPath: "inset(0 0% 0 0)" }}
        transition={{ duration: 1.3, ease: EASE }}
        className="relative hidden flex-col justify-between overflow-hidden bg-ink p-10 text-paper lg:flex xl:p-14"
      >
        <Wordmark inverted />

        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-paper/50">(Live prices — 4 marketplaces)</p>
          <h1 className="mt-6 text-[clamp(4rem,7.5vw,8rem)] font-medium leading-[0.86] tracking-[-0.055em]">
            <RevealText text="Shop" delay={0.55} />
            <span className="relative block h-[1em] overflow-hidden pb-[0.1em] font-serif font-normal italic tracking-[-0.02em] text-acid">
              <AnimatePresence initial={false}>
                <motion.span
                  key={wordIndex}
                  className="absolute left-0 top-0 whitespace-nowrap"
                  initial={{ y: "105%" }}
                  animate={{ y: "0%" }}
                  exit={{ y: "-105%" }}
                  transition={{ duration: 0.9, ease: EASE }}
                >
                  {CYCLING_WORDS[wordIndex]}
                </motion.span>
              </AnimatePresence>
            </span>
          </h1>
        </div>

        <div className="flex items-end justify-between gap-10">
          <p className="max-w-xs text-sm leading-relaxed text-paper/60">
            One search across Amazon, Flipkart, Myntra and AJIO — compared side by side, with your card&rsquo;s
            offers already applied.
          </p>
          <SpinBadge text="One search · Every store · " className="text-paper" />
        </div>

        <Marquee
          duration={26}
          className="pointer-events-none absolute inset-x-0 bottom-[38%] -rotate-6 opacity-[0.07]"
          items={MARKETPLACES.map((name) => (
            <span key={name} className="px-8 text-[9rem] font-semibold uppercase leading-none tracking-[-0.05em]">
              {name}
            </span>
          ))}
        />
      </motion.aside>

      <main className="flex flex-col px-6 py-8 sm:px-12 lg:px-16">
        <div className="lg:hidden">
          <Wordmark />
        </div>

        <div className="mx-auto my-auto w-full max-w-sm py-16">
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.45, ease: EASE }}
            >
              <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ash">
                {isRegister ? "(New here)" : "(Welcome back)"}
              </p>
              <h2 className="mt-3 text-5xl font-medium leading-[0.95] tracking-[-0.045em]">
                {isRegister ? (
                  <>
                    <RevealText text="Create" delay={0.05} />{" "}
                    <RevealText text="account" delay={0.12} className="font-serif font-normal italic tracking-[-0.02em]" />
                  </>
                ) : (
                  <>
                    <RevealText text="Sign" delay={0.05} />{" "}
                    <RevealText text="in" delay={0.12} className="font-serif font-normal italic tracking-[-0.02em]" />
                  </>
                )}
              </h2>
            </motion.div>
          </AnimatePresence>

          <form ref={formScope} onSubmit={handleSubmit} className="mt-10 flex flex-col gap-6">
            <Field
              label="Email address"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Field
              label="Password"
              type="password"
              autoComplete={isRegister ? "new-password" : "current-password"}
              required
              minLength={isRegister ? 8 : undefined}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              hint={isRegister ? "At least 8 characters" : undefined}
            />

            <AnimatePresence>
              {error && (
                <motion.p
                  role="alert"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.35, ease: EASE }}
                  className="overflow-hidden border-l-2 border-ember pl-3 text-sm text-ember"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={submitting}
              className="group mt-2 flex h-14 items-center justify-between rounded-full bg-ink pl-7 pr-2 text-[15px] font-medium text-paper transition-colors duration-500 hover:bg-acid hover:text-ink disabled:opacity-60"
            >
              <RollText>{submitting ? "One moment…" : isRegister ? "Create account" : "Sign in"}</RollText>
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-paper text-ink transition-transform duration-500 ease-expo group-hover:translate-x-0.5 group-hover:-rotate-45">
                {submitting ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink/20 border-t-ink" />
                ) : (
                  <ArrowRight className="h-4 w-4" />
                )}
              </span>
            </button>
          </form>

          <p className="mt-8 text-sm text-ash">
            {isRegister ? "Already have an account?" : "New to ScrapW?"}{" "}
            <button
              type="button"
              onClick={switchMode}
              className="bg-linear-to-r from-ink to-ink bg-[length:100%_1px] bg-left-bottom bg-no-repeat font-medium text-ink transition-[background-size] duration-500 ease-expo hover:bg-[length:0%_1px]"
            >
              {isRegister ? "Sign in" : "Create an account"}
            </button>
          </p>
        </div>

        <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ash">© {new Date().getFullYear()} ScrapW</p>
      </main>
    </div>
  );
}
