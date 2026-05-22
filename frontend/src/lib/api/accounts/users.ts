// src/lib/api/accounts/users.ts
import { requestJson } from "../core/client";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const DEFAULT_AVATAR = (username: string) =>
  `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(username || "user")}`;

export function resolveUserAvatarUrl(avatar: string | null | undefined, username: string): string {
  const value = avatar?.trim();
  if (!value) return DEFAULT_AVATAR(username);

  // Keep already-absolute or browser-generated URLs unchanged.
  if (value.startsWith("http://") || value.startsWith("https://") || value.startsWith("blob:") || value.startsWith("data:")) {
    return value;
  }

  try {
    return new URL(value, `${API_BASE_URL.replace(/\/+$/, "")}/`).toString();
  } catch {
    return DEFAULT_AVATAR(username);
  }
}

export type UserQuery = {
  plan?: "free" | "pro";
  is_active?: boolean;
  role?: "admin" | "user";
  email_verified?: boolean;
  search?: string;
  page?: number;
};

export type UserUpdatePayload = Partial<{
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  plan: "free" | "pro";
  role: "admin" | "user";
  is_active: boolean;
}>;

export type AdminCreateUserPayload = {
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  plan?: "free" | "pro";
  role?: "admin" | "user";
  is_active?: boolean;
  password?: string;
};

export type AdminUser = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  avatar?: string;
  plan: "free" | "pro";
  is_active: boolean;
  email_verified: boolean;
  role: "admin" | "user";
  created_at: string;
};

export type PaginatedUsers = {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminUser[];
};

export const listUsers = (query?: UserQuery) =>
  requestJson<PaginatedUsers>("/api/admin/users/", { query });

export const getUser = (id: number) =>
  requestJson<AdminUser>(`/api/admin/users/${id}/`);

const CREATE_USER_PATHS = [
  "/api/admin/users/",
  "/api/admin/users",
  "/api/admin/users/create/",
  "/api/admin/users/create",
  "/api/admin/users/add/",
  "/api/admin/users/add",
  "/api/admin/user/",
  "/api/admin/user",
  "/api/admin/user/create/",
  "/api/admin/user/create",
  "/api/admin/create-user/",
  "/api/admin/create-user",
  "/api/auth/register/",
  "/api/auth/signup/",
  "/api/users/register/",
  "/api/users/signup/",
];

export const createUser = async (data: AdminCreateUserPayload) => {
  let lastError: unknown;

  for (const path of CREATE_USER_PATHS) {
    try {
      return await requestJson<AdminUser>(path, {
        method: "POST",
        body: JSON.stringify(data),
      });
    } catch (error) {
      lastError = error;
      const message = error instanceof Error ? error.message.toLowerCase() : "";
      const shouldTryNext =
        message.includes("method") || message.includes("not found") || message.includes("404");

      if (!shouldTryNext) {
        throw error;
      }
    }
  }

  throw lastError instanceof Error ? lastError : new Error("Failed to create user.");
};

export const updateUser = (id: number, data: UserUpdatePayload | FormData) => {
  const isFormData = data instanceof FormData;
  return requestJson<AdminUser>(`/api/admin/users/${id}/`, {
    method: "PATCH",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  });
};

export const deleteUser = (id: number) =>
  requestJson<void>(`/api/admin/users/${id}/`, { method: "DELETE" });