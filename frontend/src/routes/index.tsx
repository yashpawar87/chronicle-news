import { useEffect, useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { keepPreviousData, queryOptions, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown } from "lucide-react";
import { CardStack } from "@/components/CardStack";
import { getFeedSections } from "@/lib/news.functions";
import type { FeedSection, NewsArticle } from "@/lib/news.types";

const feedQueryOptions = queryOptions({
  queryKey: ["rss-sections"],
  queryFn: () => getFeedSections(),
  staleTime: 5 * 60 * 1000,
});

const SECTION_TO_CATEGORY: Record<string, NewsArticle["category"]> = {
  "Top stories": "india",
  "Latest Stories": "india",
  Tech: "trending",
  "Maharashtra Marathi": "states",
  Business: "business",
  Entertainment: "trending",
  Sports: "sports",
  "Lifestyle and Fashion": "world",
  Cricket: "sports",
};

function toSwipeArticle(section: FeedSection, story: FeedSection["stories"][number]): NewsArticle {
  return {
    id: String(story.id),
    title: story.title,
    description: story.summary || "",
    link: story.url,
    image: story.imageUrl,
    imageCredit: null,
    source: story.sourceName,
    category: SECTION_TO_CATEGORY[section.section] ?? "india",
    section: section.section,
    publishedAt: story.publishedAt,
    confidence: "rss",
    rankScore: 0,
  };
}

export const Route = createFileRoute("/")({
  loader: ({ context }) => {
    context.queryClient.ensureQueryData(feedQueryOptions);
  },
  component: Index,
  head: () => ({
    meta: [
      { title: "Chronicle — Swipe the Day's News" },
      {
        name: "description",
        content:
          "Swipe through the latest RSS stories one card at a time, grouped by section.",
      },
      { property: "og:title", content: "Chronicle — Swipe the Day's News" },
      {
        property: "og:description",
        content: "A swipe deck powered by live RSS sections and story images.",
      },
      { property: "og:url", content: "/" },
    ],
    links: [{ rel: "canonical", href: "/" }],
  }),
});

function Index() {
  const queryClient = useQueryClient();
  const [selectedSection, setSelectedSection] = useState<string>("");

  const { data: sections = [], isFetching } = useQuery({
    ...feedQueryOptions,
    placeholderData: keepPreviousData,
  });

  useEffect(() => {
    if (!selectedSection && sections.length > 0) {
      setSelectedSection(sections[0].section);
    }
  }, [sections, selectedSection]);

  const currentSection = useMemo(
    () => sections.find((section) => section.section === selectedSection) ?? sections[0],
    [sections, selectedSection],
  );

  const articles = useMemo(
    () =>
      currentSection ? currentSection.stories.map((story) => toSwipeArticle(currentSection, story)) : [],
    [currentSection],
  );

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["rss-sections"] });
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <span className="font-serif text-2xl tracking-tight">CHRONICLE</span>
          <nav className="hidden items-center gap-8 md:flex" aria-label="Sections">
            {sections.map((section, i) => (
              <button
                key={section.section}
                type="button"
                onClick={() => setSelectedSection(section.section)}
                className={`cursor-pointer text-sm ${
                  i === 0
                    ? "border-b border-foreground pb-1 text-foreground"
                    : selectedSection === section.section
                      ? "border-b border-foreground pb-1 text-foreground"
                      : "text-muted-foreground"
                }`}
              >
                {section.section}
              </button>
            ))}
          </nav>
          <span className="w-6 md:hidden" aria-hidden="true" />
        </div>
      </header>

      <div className="border-b border-border py-5">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-3">
            {sections.map((section) => (
              <button
                key={section.section}
                type="button"
                onClick={() => setSelectedSection(section.section)}
                className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                  selectedSection === section.section
                    ? "border-foreground bg-foreground text-background"
                    : "border-border bg-card text-foreground hover:border-foreground/40"
                }`}
              >
                {section.section}
              </button>
            ))}
          </div>
        </div>
      </div>

      <main className="flex flex-1 flex-col items-center px-6 pb-14 pt-10 sm:pt-14">
        <h1 className="sr-only">Chronicle — swipe the day's RSS stories</h1>

        <CardStack articles={articles} onRefresh={refresh} refreshing={isFetching} />

        <p className="mt-8 text-sm text-muted-foreground">
          Swipe left to go previous and right to go next in the circular deck. Use the open
          button on the card to read the full story.
        </p>

        <button
          type="button"
          onClick={refresh}
          disabled={isFetching}
          className="mt-6 inline-flex items-center gap-2 rounded-full border border-border bg-card px-6 py-2.5 text-sm font-medium transition-colors hover:border-foreground/40 disabled:opacity-50"
        >
          Reload feeds
          <ChevronDown className="h-4 w-4" />
        </button>
      </main>

      <footer className="border-t border-border bg-muted/40 py-10">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <p className="font-serif text-3xl">Chronicle</p>
          <p className="mt-6 text-xs text-muted-foreground">
            © 2026 Chronicle Editorial. Swiping live stories from today.
          </p>
        </div>
      </footer>
    </div>
  );
}
