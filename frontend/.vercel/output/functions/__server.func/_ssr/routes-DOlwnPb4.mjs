import { t as getServerFnById } from "../__23tanstack-start-server-fn-resolver-BvDeIxUw.mjs";
import { c as createServerFn, i as TSS_SERVER_FUNCTION } from "./createServerFn-CIHAFgYl.mjs";
import { t as queryOptions } from "../_libs/react+tanstack__react-query.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-DOlwnPb4.js
var createSsrRpc = (functionId) => {
	const url = "/_serverFn/" + functionId;
	const serverFnMeta = { id: functionId };
	const fn = async (...args) => {
		return (await getServerFnById(functionId, { origin: "server" }))(...args);
	};
	return Object.assign(fn, {
		url,
		serverFnMeta,
		[TSS_SERVER_FUNCTION]: true
	});
};
var getFeedSections = createServerFn({ method: "GET" }).handler(createSsrRpc("43c04d14a336a362111e97ea5b1149aff31d80f39b900ae7c5a686724d993c6b"));
var feedQueryOptions = queryOptions({
	queryKey: ["rss-sections"],
	queryFn: () => getFeedSections(),
	staleTime: 300 * 1e3
});
//#endregion
export { feedQueryOptions as t };
