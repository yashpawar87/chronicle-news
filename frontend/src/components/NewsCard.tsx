import type { NewsArticle } from "@/lib/news.types";
import { ArrowUpRight } from "lucide-react";

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function NewsCard({
  article,
  onOpen,
}: {
  article: NewsArticle;
  onOpen?: () => void;
}) {
  const ago = timeAgo(article.publishedAt);

  return (
    <article className="relative flex h-full flex-col overflow-hidden rounded-[20px] bg-card shadow-[0_18px_50px_-24px_rgba(30,30,40,0.35)] ring-1 ring-border">
      <div className="h-56 shrink-0 overflow-hidden bg-muted sm:h-64">
        {article.image ? (
          <img
            src={article.image}
            alt={article.title}
            className="h-full w-full object-cover"
            draggable={false}
            loading="eager"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <span className="font-serif text-3xl text-muted-foreground/50">Chronicle</span>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col px-6 pb-5 pt-5 sm:px-8">
        {onOpen && (
          <button
            type="button"
            onPointerDown={(event) => event.stopPropagation()}
            onClick={onOpen}
            className="absolute right-4 top-4 z-10 inline-flex h-9 items-center gap-1 rounded-full border border-border bg-background/95 px-3 text-xs font-medium text-foreground shadow-sm backdrop-blur transition-colors hover:border-foreground/40"
          >
            Open
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        )}

        <div className="flex items-center gap-3">
          <span className="rounded-full border border-border px-3 py-1 text-xs font-medium text-foreground">
            {article.section}
          </span>
          {ago && <span className="text-xs text-muted-foreground">{ago}</span>}
        </div>

        <h2 className="mt-4 font-serif text-[1.7rem] leading-[1.1] tracking-tight sm:text-[2rem]">
          {article.title}
        </h2>

        {article.description && (
          <p className="mt-3 line-clamp-3 font-serif text-base leading-snug text-muted-foreground sm:text-lg">
            {article.description}
          </p>
        )}

        <div className="mt-auto pt-5">
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
            {article.source}
          </p>
        </div>
      </div>
    </article>
  );
}
