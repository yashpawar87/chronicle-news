import { createServerFn } from "@tanstack/react-start";

export const getFeedSections = createServerFn({ method: "GET" }).handler(async () => {
  const { getFeedSections } = await import("./news.server");
  return getFeedSections();
});
