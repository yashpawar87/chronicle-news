export const CATEGORIES = ["india", "politics", "states", "business", "sports", "world", "trending"] as const;

export type Category = (typeof CATEGORIES)[number];

export const CATEGORY_LABELS: Record<Category, string> = {
  india: "India",
  politics: "Politics",
  states: "States",
  sports: "Sports",
  business: "Business",
  world: "World",
  trending: "Trending",
};

export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  link: string;
  image: string | null;
  imageCredit: string | null;
  source: string;
  category: Category;
  section: string;
  publishedAt: string | null;
  confidence: string;
  rankScore: number;
}

export interface FeedStory {
  id: number;
  title: string;
  summary: string | null;
  url: string;
  imageUrl: string | null;
  publishedAt: string | null;
  sourceName: string;
}

export interface FeedSection {
  section: string;
  feedUrl: string | null;
  stories: FeedStory[];
}
