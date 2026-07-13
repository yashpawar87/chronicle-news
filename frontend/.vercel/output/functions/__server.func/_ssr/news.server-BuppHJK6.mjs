//#region node_modules/.nitro/vite/services/ssr/assets/news.server-BuppHJK6.js
var API_BASE = process.env.BACKEND_API_BASE || "";
function fetchJson(path) {
	if (!API_BASE) throw new Error("BACKEND_API_BASE is not configured. Set it in your Vercel environment variables to the deployed API URL.");
	return fetch(new URL(path, API_BASE).toString(), {
		headers: { Accept: "application/json" },
		signal: AbortSignal.timeout(1e4)
	}).then(async (res) => {
		if (!res.ok) throw new Error(`Backend request failed: ${res.status} ${path}`);
		return res.json();
	});
}
function toFeedStory(story) {
	return {
		id: story.id,
		title: story.title,
		summary: story.summary || null,
		url: story.url,
		imageUrl: story.image_url || null,
		publishedAt: story.published_at || null,
		sourceName: story.source_name
	};
}
async function getFeedSections() {
	return (await fetchJson("/feeds/sections")).map((section) => ({
		section: section.section,
		feedUrl: section.feed_url || null,
		stories: section.stories.map(toFeedStory)
	}));
}
//#endregion
export { getFeedSections };
