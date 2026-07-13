import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion, useMotionValue, useTransform } from "motion/react";
import { RefreshCw, RotateCcw, RotateCw } from "lucide-react";
import type { NewsArticle } from "@/lib/news.types";
import { NewsCard } from "./NewsCard";

const THRESHOLD = 120;

interface CardStackProps {
  articles: NewsArticle[];
  onRefresh: () => void;
  refreshing?: boolean;
}

export function CardStack({ articles, onRefresh, refreshing }: CardStackProps) {
  const [deck, setDeck] = useState<NewsArticle[]>(articles);
  const [exitDir, setExitDir] = useState<1 | -1>(1);

  useEffect(() => {
    setDeck(articles);
  }, [articles]);

  const current = deck[0];

  const decide = useCallback(
    (dir: 1 | -1) => {
      setDeck((prev) => {
        if (prev.length <= 1) return prev;
        return dir === 1
          ? [...prev.slice(1), prev[0]]
          : [prev[prev.length - 1], ...prev.slice(0, -1)];
      });
      setExitDir(dir);
    },
    [],
  );

  const openCurrent = useCallback(() => {
    const article = deck[0];
    if (!article) return;
    window.open(article.link, "_blank", "noopener,noreferrer");
  }, [deck]);

  const isEmpty = deck.length === 0;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") decide(-1);
      if (e.key === "ArrowRight") decide(1);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [decide]);

  if (isEmpty) {
    return (
      <div className="mx-auto flex h-[540px] w-full max-w-xl flex-col items-center justify-center rounded-[20px] border border-dashed border-border bg-card/50 px-8 text-center sm:h-[580px]">
        <h2 className="font-serif text-4xl">You're all caught up.</h2>
        <p className="mt-3 text-sm text-muted-foreground">
          Every story in this section has been read.
        </p>
        <button
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
          Reload feeds
        </button>
      </div>
    );
  }

  return (
    <div className="relative mx-auto w-full max-w-xl">
      <div className="relative h-[540px] sm:h-[580px]">
        {/* Back cards peeking out */}
        {deck[2] && (
          <div
            className="pointer-events-none absolute inset-0 origin-bottom"
            style={{ transform: "translateY(24px) scale(0.92)", opacity: 0.5 }}
          >
            <NewsCard article={deck[2]} onOpen={openCurrent} />
          </div>
        )}
        {deck[1] && (
          <div
            className="pointer-events-none absolute inset-0 origin-bottom"
            style={{ transform: "translateY(12px) scale(0.96)", opacity: 0.8 }}
          >
            <NewsCard article={deck[1]} onOpen={openCurrent} />
          </div>
        )}

        <AnimatePresence custom={exitDir} initial={false}>
          <SwipeCard key={current.id} article={current} onDecide={decide} onOpen={openCurrent} />
        </AnimatePresence>
      </div>

      {/* Side action buttons */}
      <button
        type="button"
        onClick={() => decide(-1)}
        aria-label="Previous story"
        className="absolute left-2 top-52 z-20 flex h-14 w-14 items-center justify-center rounded-full bg-card text-foreground shadow-[0_10px_30px_-10px_rgba(30,30,40,0.4)] ring-1 ring-border transition-transform hover:scale-105 sm:-left-7 sm:top-56"
      >
        <RotateCcw className="h-5 w-5" />
      </button>
      <button
        type="button"
        onClick={() => decide(1)}
        aria-label="Next story"
        className="absolute right-2 top-52 z-20 flex h-14 w-14 items-center justify-center rounded-full bg-card text-foreground shadow-[0_10px_30px_-10px_rgba(30,30,40,0.4)] ring-1 ring-border transition-transform hover:scale-105 sm:-right-7 sm:top-56"
      >
        <RotateCw className="h-5 w-5" />
      </button>
    </div>
  );
}

function SwipeCard({
  article,
  onDecide,
  onOpen,
}: {
  article: NewsArticle;
  onDecide: (dir: 1 | -1) => void;
  onOpen: () => void;
}) {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-300, 300], [-8, 8]);
  const dismissOpacity = useTransform(x, [-THRESHOLD, -40], [1, 0]);
  const shuffleOpacity = useTransform(x, [40, THRESHOLD], [0, 1]);

  return (
    <motion.div
      className="absolute inset-0 cursor-grab touch-none active:cursor-grabbing"
      style={{ x, rotate }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.9}
      onDragEnd={(_, info) => {
        if (info.offset.x > THRESHOLD) onDecide(1);
        else if (info.offset.x < -THRESHOLD) onDecide(-1);
      }}
      variants={{
        exit: (dir: number) => ({
          x: (dir || 1) * 640,
          rotate: (dir || 1) * 14,
          opacity: 0,
          transition: { duration: 0.35, ease: "easeOut" as const },
        }),
      }}
      exit="exit"
      transition={{ type: "spring", stiffness: 300, damping: 28 }}
    >
      <NewsCard article={article} onOpen={onOpen} />

      {/* Drag intent overlays */}
      <motion.div
        style={{ opacity: dismissOpacity }}
        className="pointer-events-none absolute left-6 top-6 rounded-full bg-destructive px-5 py-2 text-sm font-semibold uppercase tracking-widest text-destructive-foreground"
      >
        Previous
      </motion.div>
      <motion.div
        style={{ opacity: shuffleOpacity }}
        className="pointer-events-none absolute right-6 top-6 rounded-full bg-success px-5 py-2 text-sm font-semibold uppercase tracking-widest text-success-foreground"
      >
        Next
      </motion.div>
    </motion.div>
  );
}
