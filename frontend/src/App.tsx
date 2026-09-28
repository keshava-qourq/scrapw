import { AnimatePresence, MotionConfig, motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";
import { useRoute } from "./router";
import { AUTH_EXPIRED_EVENT, getCurrentUser, logout } from "./api";
import Footer from "./components/Footer";
import Header, { type Tab } from "./components/Header";
import LiveSearchView from "./components/LiveSearchView";
import LoginView from "./components/LoginView";
import WatchlistView from "./components/WatchlistView";
import Cursor from "./components/ui/Cursor";
import Intro from "./components/ui/Intro";
import Wordmark from "./components/ui/Wordmark";
import { EASE, scrollToTop, shouldPlayIntro, startSmoothScroll } from "./components/ui/motion";
import type { User } from "./types";

export default function App() {
  const { route, navigate, goBack } = useRoute();
  const tab = route.view;
  const [user, setUser] = useState<User | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [playingIntro, setPlayingIntro] = useState(shouldPlayIntro);
  const finishIntro = useCallback(() => setPlayingIntro(false), []);

  useEffect(() => startSmoothScroll(), []);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setCheckingSession(false));

    const handleExpired = () => setUser(null);
    window.addEventListener(AUTH_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleExpired);
  }, []);

  function handleLogout() {
    logout();
    setUser(null);
  }

  // Tabs (and the logo) always land on the top of a view — "Home" also clears any search.
  function handleTabChange(next: Tab) {
    scrollToTop();
    navigate({ view: next, q: null, page: 1 });
  }

  const handleSearchNavigate = useCallback(
    (q: string | null, page: number, replace = false) => navigate({ view: "live", q, page }, { replace }),
    [navigate],
  );

  // While the intro plays nothing mounts underneath, so each screen's entrance animations run as the curtain lifts.
  const screen = playingIntro ? "intro" : checkingSession ? "splash" : user ? "app" : "login";

  return (
    <MotionConfig reducedMotion="user">
      <div className="grain min-h-screen overflow-x-clip">
        <Cursor />
        <AnimatePresence>{playingIntro && <Intro key="intro" onDone={finishIntro} />}</AnimatePresence>
        <AnimatePresence mode="wait">
          {screen === "splash" && (
            <motion.div
              key="splash"
              exit={{ opacity: 0 }}
              className="flex min-h-screen items-center justify-center"
            >
              <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1.6, repeat: Infinity }}>
                <Wordmark />
              </motion.div>
            </motion.div>
          )}

          {screen === "login" && (
            <motion.div key="login" exit={{ opacity: 0, scale: 0.98 }} transition={{ duration: 0.5, ease: EASE }}>
              <LoginView onAuthenticated={setUser} />
            </motion.div>
          )}

          {screen === "app" && user && (
            <motion.div
              key="app"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6, ease: EASE }}
            >
              <Header tab={tab} onTabChange={handleTabChange} user={user} onLogout={handleLogout} />
              <AnimatePresence mode="wait">
                <motion.main
                  key={tab}
                  initial={{ opacity: 0, y: 28, filter: "blur(10px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  exit={{ opacity: 0, y: -18, filter: "blur(8px)" }}
                  transition={{ duration: 0.65, ease: EASE }}
                >
                  {tab === "compare" ? (
                    <WatchlistView />
                  ) : (
                    <LiveSearchView
                      routeQuery={route.q}
                      routePage={route.page}
                      onNavigate={handleSearchNavigate}
                      onBack={goBack}
                    />
                  )}
                </motion.main>
              </AnimatePresence>
              <Footer />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </MotionConfig>
  );
}
