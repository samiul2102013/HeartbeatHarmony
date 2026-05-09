const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

import {
  getAdminAccessToken,
  getAdminRefreshToken,
  clearAdminSession,
  updateAdminAccessToken,
} from "./tokens";

function buildUrl(
  path: string,
  query?: Record<string, string | number | boolean | null | undefined>
) {
  const base = API_BASE_URL.replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${base}${normalizedPath}`);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") return;
      url.searchParams.set(key, String(value));
    });
  }
  return url.toString();
}

function normalizeError(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== "object") return fallback;
  const data = payload as Record<string, any>;
  if (typeof data.detail === "string") return data.detail;
  for (const value of Object.values(data)) {
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    if (typeof value === "string") return value;
  }
  return fallback;
}

async function refreshAdminAccess(): Promise<string> {
  const refresh = getAdminRefreshToken();
  if (!refresh) throw new Error("No refresh token");

  const response = await fetch(`${API_BASE_URL}/api/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) throw new Error("Refresh failed");

  const data = await response.json();
  const newAccess = data.access;
  if (!newAccess) throw new Error("No access token in refresh response");
  updateAdminAccessToken(newAccess);
  return newAccess;
}

// Public paths that should never send an Authorization header
const PUBLIC_PATHS = [
  "/api/auth/login/",
  "/api/auth/token/refresh/",
  "/api/auth/forgot-password/",
  "/api/auth/reset-password/",
  "/api/auth/verify-email/",
];

export async function requestJson<T = unknown>(
  path: string,
  options: RequestInit & {
    query?: Record<string, string | number | boolean | null | undefined>;
    skipContentType?: boolean;
    skipAuth?: boolean;
  } = {}
): Promise<T> {
  const { query, headers, body, skipContentType, skipAuth, ...rest } = options;

  const isPublic = skipAuth || PUBLIC_PATHS.some((p) => path.startsWith(p));

  const buildHeaders = (token: string | null) => {
    const h = new Headers(headers);
    // Never send auth header for public/login endpoints
    if (token && !isPublic) {
      h.set("Authorization", `Bearer ${token}`);
    }
    if (body && !(body instanceof FormData) && !skipContentType) {
      h.set("Content-Type", "application/json");
    }
    return h;
  };

  const url = buildUrl(path, query);
  const token = getAdminAccessToken();

  let response = await fetch(url, {
    ...rest,
    headers: buildHeaders(token),
    body,
  });

  // Only attempt refresh for protected endpoints
  if (response.status === 401 && !isPublic) {
    try {
      const newToken = await refreshAdminAccess();
      response = await fetch(url, {
        ...rest,
        headers: buildHeaders(newToken),
        body,
      });
    } catch {
      clearAdminSession();
      if (typeof window !== "undefined") {
        window.location.href = "/signin";
      }
      throw new Error("Session expired. Please login again.");
    }
  }

  // 204 No Content (DELETE)
  if (response.status === 204) return null as T;

  const text = await response.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new Error(normalizeError(payload, `${response.status} ${response.statusText}`));
  }

  return payload as T;
}