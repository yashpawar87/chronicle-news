import { createStart, createMiddleware, createCsrfMiddleware } from "@tanstack/react-start";

import { renderErrorPage } from "./lib/error-page";

const backendBase = process.env.BACKEND_API_BASE || "http://127.0.0.1:8001";

const backendProxyMiddleware = createMiddleware().server(async ({ next, request }) => {
  const url = new URL(request.url);
  const isBackendRoute =
    url.pathname === "/health" ||
    url.pathname.startsWith("/feeds/") ||
    url.pathname.startsWith("/admin/");

  if (isBackendRoute) {
    const backendUrl = new URL(`${url.pathname}${url.search}`, backendBase);
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: request.headers,
    });
    return response;
  }

  return next();
});

const errorMiddleware = createMiddleware().server(async ({ next }) => {
  try {
    return await next();
  } catch (error) {
    if (error != null && typeof error === "object" && "statusCode" in error) {
      throw error;
    }
    console.error(error);
    return new Response(renderErrorPage(), {
      status: 500,
      headers: { "content-type": "text/html; charset=utf-8" },
    });
  }
});

const csrfMiddleware = createCsrfMiddleware({
  filter: (ctx) => ctx.handlerType === "serverFn",
});

export const startInstance = createStart(() => ({
  requestMiddleware: [backendProxyMiddleware, csrfMiddleware, errorMiddleware],
}));
