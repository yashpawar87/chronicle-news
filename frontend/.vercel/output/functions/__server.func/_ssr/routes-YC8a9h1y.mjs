import { s as __toESM } from "../__23tanstack-start-server-fn-resolver-BvDeIxUw.mjs";
import { a as keepPreviousData } from "../_libs/tanstack__query-core.mjs";
import { a as require_jsx_runtime, i as useQueryClient, n as useQuery, o as require_react } from "../_libs/react+tanstack__react-query.mjs";
import { t as feedQueryOptions } from "./routes-DOlwnPb4.mjs";
import { a as ArrowUpRight, i as ChevronDown, n as RotateCcw, r as RefreshCw, t as RotateCw } from "../_libs/lucide-react.mjs";
import { i as AnimatePresence, n as useMotionValue, t as useTransform } from "../_libs/framer-motion.mjs";
import { t as motion } from "../_libs/motion.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-YC8a9h1y.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function timeAgo(iso) {
	if (!iso) return "";
	const diff = Date.now() - new Date(iso).getTime();
	const mins = Math.floor(diff / 6e4);
	if (mins < 1) return "just now";
	if (mins < 60) return `${mins}m ago`;
	const hours = Math.floor(mins / 60);
	if (hours < 24) return `${hours}h ago`;
	return `${Math.floor(hours / 24)}d ago`;
}
function NewsCard({ article, onOpen }) {
	const ago = timeAgo(article.publishedAt);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
		className: "relative flex h-full flex-col overflow-hidden rounded-[20px] bg-card shadow-[0_18px_50px_-24px_rgba(30,30,40,0.35)] ring-1 ring-border",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "h-56 shrink-0 overflow-hidden bg-muted sm:h-64",
			children: article.image ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("img", {
				src: article.image,
				alt: article.title,
				className: "h-full w-full object-cover",
				draggable: false,
				loading: "eager"
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex h-full w-full items-center justify-center",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-serif text-3xl text-muted-foreground/50",
					children: "Chronicle"
				})
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-1 flex-col px-6 pb-5 pt-5 sm:px-8",
			children: [
				onOpen && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
					type: "button",
					onPointerDown: (event) => event.stopPropagation(),
					onClick: onOpen,
					className: "absolute right-4 top-4 z-10 inline-flex h-9 items-center gap-1 rounded-full border border-border bg-background/95 px-3 text-xs font-medium text-foreground shadow-sm backdrop-blur transition-colors hover:border-foreground/40",
					children: ["Open", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpRight, { className: "h-3.5 w-3.5" })]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "rounded-full border border-border px-3 py-1 text-xs font-medium text-foreground",
						children: article.section
					}), ago && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-xs text-muted-foreground",
						children: ago
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "mt-4 font-serif text-[1.7rem] leading-[1.1] tracking-tight sm:text-[2rem]",
					children: article.title
				}),
				article.description && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 line-clamp-3 font-serif text-base leading-snug text-muted-foreground sm:text-lg",
					children: article.description
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-auto pt-5",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground",
						children: article.source
					})
				})
			]
		})]
	});
}
var THRESHOLD = 120;
function CardStack({ articles, onRefresh, refreshing }) {
	const [deck, setDeck] = (0, import_react.useState)(articles);
	const [exitDir, setExitDir] = (0, import_react.useState)(1);
	(0, import_react.useEffect)(() => {
		setDeck(articles);
	}, [articles]);
	const current = deck[0];
	const decide = (0, import_react.useCallback)((dir) => {
		setDeck((prev) => {
			if (prev.length <= 1) return prev;
			return dir === 1 ? [...prev.slice(1), prev[0]] : [prev[prev.length - 1], ...prev.slice(0, -1)];
		});
		setExitDir(dir);
	}, []);
	const openCurrent = (0, import_react.useCallback)(() => {
		const article = deck[0];
		if (!article) return;
		window.open(article.link, "_blank", "noopener,noreferrer");
	}, [deck]);
	const isEmpty = deck.length === 0;
	(0, import_react.useEffect)(() => {
		const handler = (e) => {
			if (e.key === "ArrowLeft") decide(-1);
			if (e.key === "ArrowRight") decide(1);
		};
		window.addEventListener("keydown", handler);
		return () => window.removeEventListener("keydown", handler);
	}, [decide]);
	if (isEmpty) return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto flex h-[540px] w-full max-w-xl flex-col items-center justify-center rounded-[20px] border border-dashed border-border bg-card/50 px-8 text-center sm:h-[580px]",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-serif text-4xl",
				children: "You're all caught up."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-sm text-muted-foreground",
				children: "Every story in this section has been read."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
				type: "button",
				onClick: onRefresh,
				disabled: refreshing,
				className: "mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: `h-4 w-4 ${refreshing ? "animate-spin" : ""}` }), "Reload feeds"]
			})
		]
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "relative mx-auto w-full max-w-xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "relative h-[540px] sm:h-[580px]",
				children: [
					deck[2] && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "pointer-events-none absolute inset-0 origin-bottom",
						style: {
							transform: "translateY(24px) scale(0.92)",
							opacity: .5
						},
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(NewsCard, {
							article: deck[2],
							onOpen: openCurrent
						})
					}),
					deck[1] && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "pointer-events-none absolute inset-0 origin-bottom",
						style: {
							transform: "translateY(12px) scale(0.96)",
							opacity: .8
						},
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(NewsCard, {
							article: deck[1],
							onOpen: openCurrent
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatePresence, {
						custom: exitDir,
						initial: false,
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SwipeCard, {
							article: current,
							onDecide: decide,
							onOpen: openCurrent
						}, current.id)
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: () => decide(-1),
				"aria-label": "Previous story",
				className: "absolute left-2 top-52 z-20 flex h-14 w-14 items-center justify-center rounded-full bg-card text-foreground shadow-[0_10px_30px_-10px_rgba(30,30,40,0.4)] ring-1 ring-border transition-transform hover:scale-105 sm:-left-7 sm:top-56",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RotateCcw, { className: "h-5 w-5" })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				type: "button",
				onClick: () => decide(1),
				"aria-label": "Next story",
				className: "absolute right-2 top-52 z-20 flex h-14 w-14 items-center justify-center rounded-full bg-card text-foreground shadow-[0_10px_30px_-10px_rgba(30,30,40,0.4)] ring-1 ring-border transition-transform hover:scale-105 sm:-right-7 sm:top-56",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RotateCw, { className: "h-5 w-5" })
			})
		]
	});
}
function SwipeCard({ article, onDecide, onOpen }) {
	const x = useMotionValue(0);
	const rotate = useTransform(x, [-300, 300], [-8, 8]);
	const dismissOpacity = useTransform(x, [-120, -40], [1, 0]);
	const shuffleOpacity = useTransform(x, [40, THRESHOLD], [0, 1]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
		className: "absolute inset-0 cursor-grab touch-none active:cursor-grabbing",
		style: {
			x,
			rotate
		},
		drag: "x",
		dragConstraints: {
			left: 0,
			right: 0
		},
		dragElastic: .9,
		onDragEnd: (_, info) => {
			if (info.offset.x > THRESHOLD) onDecide(1);
			else if (info.offset.x < -120) onDecide(-1);
		},
		variants: { exit: (dir) => ({
			x: (dir || 1) * 640,
			rotate: (dir || 1) * 14,
			opacity: 0,
			transition: {
				duration: .35,
				ease: "easeOut"
			}
		}) },
		exit: "exit",
		transition: {
			type: "spring",
			stiffness: 300,
			damping: 28
		},
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NewsCard, {
				article,
				onOpen
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
				style: { opacity: dismissOpacity },
				className: "pointer-events-none absolute left-6 top-6 rounded-full bg-destructive px-5 py-2 text-sm font-semibold uppercase tracking-widest text-destructive-foreground",
				children: "Previous"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
				style: { opacity: shuffleOpacity },
				className: "pointer-events-none absolute right-6 top-6 rounded-full bg-success px-5 py-2 text-sm font-semibold uppercase tracking-widest text-success-foreground",
				children: "Next"
			})
		]
	});
}
var SECTION_TO_CATEGORY = {
	"Top stories": "india",
	"Latest Stories": "india",
	Tech: "trending",
	"Maharashtra Marathi": "states",
	Business: "business",
	Entertainment: "trending",
	Sports: "sports",
	"Lifestyle and Fashion": "world",
	Cricket: "sports"
};
function toSwipeArticle(section, story) {
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
		rankScore: 0
	};
}
function Index() {
	const queryClient = useQueryClient();
	const [selectedSection, setSelectedSection] = (0, import_react.useState)("");
	const { data: sections = [], isFetching } = useQuery({
		...feedQueryOptions,
		placeholderData: keepPreviousData
	});
	(0, import_react.useEffect)(() => {
		if (!selectedSection && sections.length > 0) setSelectedSection(sections[0].section);
	}, [sections, selectedSection]);
	const currentSection = (0, import_react.useMemo)(() => sections.find((section) => section.section === selectedSection) ?? sections[0], [sections, selectedSection]);
	const articles = (0, import_react.useMemo)(() => currentSection ? currentSection.stories.map((story) => toSwipeArticle(currentSection, story)) : [], [currentSection]);
	const refresh = () => {
		queryClient.invalidateQueries({ queryKey: ["rss-sections"] });
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex min-h-screen flex-col bg-background",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("header", {
				className: "border-b border-border",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mx-auto flex max-w-6xl items-center justify-between px-6 py-5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-serif text-2xl tracking-tight",
							children: "CHRONICLE"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
							className: "hidden items-center gap-8 md:flex",
							"aria-label": "Sections",
							children: sections.map((section, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
								type: "button",
								onClick: () => setSelectedSection(section.section),
								className: `cursor-pointer text-sm ${i === 0 ? "border-b border-foreground pb-1 text-foreground" : selectedSection === section.section ? "border-b border-foreground pb-1 text-foreground" : "text-muted-foreground"}`,
								children: section.section
							}, section.section))
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "w-6 md:hidden",
							"aria-hidden": "true"
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "border-b border-border py-5",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mx-auto flex max-w-6xl flex-col gap-4 px-6 lg:flex-row lg:items-center lg:justify-between",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "flex flex-wrap gap-3",
						children: sections.map((section) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setSelectedSection(section.section),
							className: `rounded-full border px-4 py-2 text-sm transition-colors ${selectedSection === section.section ? "border-foreground bg-foreground text-background" : "border-border bg-card text-foreground hover:border-foreground/40"}`,
							children: section.section
						}, section.section))
					})
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
				className: "flex flex-1 flex-col items-center px-6 pb-14 pt-10 sm:pt-14",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "sr-only",
						children: "Chronicle — swipe the day's RSS stories"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardStack, {
						articles,
						onRefresh: refresh,
						refreshing: isFetching
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-8 text-sm text-muted-foreground",
						children: "Swipe left to go previous and right to go next in the circular deck. Use the open button on the card to read the full story."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
						type: "button",
						onClick: refresh,
						disabled: isFetching,
						className: "mt-6 inline-flex items-center gap-2 rounded-full border border-border bg-card px-6 py-2.5 text-sm font-medium transition-colors hover:border-foreground/40 disabled:opacity-50",
						children: ["Reload feeds", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-4 w-4" })]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("footer", {
				className: "border-t border-border bg-muted/40 py-10",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mx-auto max-w-6xl px-6 text-center",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-serif text-3xl",
						children: "Chronicle"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-6 text-xs text-muted-foreground",
						children: "© 2026 Chronicle Editorial. Swiping live stories from today."
					})]
				})
			})
		]
	});
}
//#endregion
export { Index as component };
