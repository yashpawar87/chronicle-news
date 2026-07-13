import { c as createServerFn, i as TSS_SERVER_FUNCTION } from "./createServerFn-CIHAFgYl.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/news.functions-BxaG_iFh.js
var createServerRpc = (serverFnMeta, splitImportFn) => {
	const url = "/_serverFn/" + serverFnMeta.id;
	return Object.assign(splitImportFn, {
		url,
		serverFnMeta,
		[TSS_SERVER_FUNCTION]: true
	});
};
var getFeedSections_createServerFn_handler = createServerRpc({
	id: "43c04d14a336a362111e97ea5b1149aff31d80f39b900ae7c5a686724d993c6b",
	name: "getFeedSections",
	filename: "src/lib/news.functions.ts"
}, (opts) => getFeedSections.__executeServer(opts));
var getFeedSections = createServerFn({ method: "GET" }).handler(getFeedSections_createServerFn_handler, async () => {
	const { getFeedSections } = await import("./news.server-BuppHJK6.mjs");
	return getFeedSections();
});
//#endregion
export { getFeedSections_createServerFn_handler };
