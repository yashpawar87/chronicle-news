import type { FeedSection, FeedStory } from "./news.types";

const API_BASE =
  process.env.BACKEND_API_BASE ||
  (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");

interface ApiFeedStory {
  id: number;
  title: string;
  summary?: string | null;
  url: string;
  image_url?: string | null;
  published_at?: string | null;
  source_name: string;
}

interface ApiFeedSection {
  section: string;
  feed_url?: string | null;
  stories: ApiFeedStory[];
}

function fetchJson<T>(path: string): Promise<T> {
  if (!API_BASE) {
    throw new Error(
      "BACKEND_API_BASE is not configured. Set it to your backend URL, such as http://127.0.0.1:8001 in Docker or your deployed API URL in production.",
    );
  }

  return fetch(new URL(path, API_BASE).toString(), {
    headers: { Accept: "application/json" },
    signal: AbortSignal.timeout(10000),
  }).then(async (res) => {
    if (!res.ok) {
      throw new Error(`Backend request failed: ${res.status} ${path}`);
    }
    return res.json() as Promise<T>;
  });
}

function toFeedStory(story: ApiFeedStory): FeedStory {
  return {
    id: story.id,
    title: story.title,
    summary: story.summary || null,
    url: story.url,
    imageUrl: story.image_url || null,
    publishedAt: story.published_at || null,
    sourceName: story.source_name,
  };
}

export async function getFeedSections(): Promise<FeedSection[]> {
  const sections = await fetchJson<ApiFeedSection[]>("/feeds/sections");
  return sections.map((section) => ({
    section: section.section,
    feedUrl: section.feed_url || null,
    stories: section.stories.map(toFeedStory),
  }));
}
