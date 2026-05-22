import { requestJson } from "../core/client";
import { setAdminSession, clearAdminSession } from "../core/tokens";

export type AdminLoginResponse = { access: string; refresh?: string };

function findStringByKeys(value: unknown, keys: string[], depth = 0): string | undefined {
  if (!value || typeof value !== "object" || depth > 4) return undefined;

  const record = value as Record<string, unknown>;
  for (const key of keys) {
    const candidate = record[key];
    if (typeof candidate === "string" && candidate.trim()) return candidate;
  }

  for (const nested of Object.values(record)) {
    const found = findStringByKeys(nested, keys, depth + 1);
    if (found) return found;
  }

  return undefined;
}

function resolveLoginResponse(payload: unknown): AdminLoginResponse {
  const data = payload as Record<string, any> | null;
  const access =
    findStringByKeys(data, [
      "access",
      "access_token",
      "accessToken",
      "token",
      "jwt",
      "auth_token",
    ]) ??
    data?.access ??
    data?.access_token ??
    data?.accessToken ??
    data?.token;
  const refresh =
    findStringByKeys(data, [
      "refresh",
      "refresh_token",
      "refreshToken",
      "refresh_token",
      "refreshToken",
    ]) ??
    data?.refresh ??
    data?.refresh_token ??
    data?.refreshToken;

  if (typeof access !== "string") {
    throw new Error("Login response did not include an access token.");
  }

  return typeof refresh === "string" ? { access, refresh } : { access };
}

export async function loginAdmin(email: string, password: string) {
  const res = await requestJson<unknown>("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  const tokens = resolveLoginResponse(res);
  setAdminSession(tokens.access, tokens.refresh);
  return tokens;
}
 
export async function refreshToken(refresh: string) {
  return requestJson<{ access: string }>("/api/auth/token/refresh/", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });
}
 
export function logoutAdmin() {
  clearAdminSession();
  if (typeof window !== "undefined") window.location.href = "/signin";
}

export async function requestPasswordReset(email: string) {
  return requestJson("/api/auth/forgot-password/", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function verifyEmail(token: string) {
  return requestJson("/api/auth/verify-email/", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export async function resetPassword(token: string, newPassword: string) {
  return requestJson("/api/auth/reset-password/", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

export const getCurrentUser = () =>
  requestJson("/api/auth/me/");