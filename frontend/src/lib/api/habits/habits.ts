import { requestJson } from "../core/client";

const extractData = (res: any) => res?.data ?? res;

export type HabitQuery = {
  category?: number;
  is_active?: boolean;
  search?: string;
  page?: number;
};

export const listHabits = (query?: HabitQuery) =>
  requestJson("/api/admin/habits/", { query }).then(extractData);

export type AdminHabitPayload = {
  category: number;
  activity_name: string;
  description?: string;
  duration?: number | null;
  is_active?: boolean;
  schedule_time?: string | null;
};

export const listAdminHabits = (query?: HabitQuery) =>
  requestJson("/api/admin/habits/", { query }).then(extractData);

export const createAdminHabit = (data: AdminHabitPayload) =>
  requestJson("/api/admin/habits/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);

export const updateAdminHabit = (id: number, data: Partial<AdminHabitPayload>) =>
  requestJson(`/api/admin/habits/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);

export const deleteAdminHabit = (id: number) =>
  requestJson(`/api/admin/habits/${id}/`, { method: "DELETE" });

// ── User habits (mobile feed) ───────────────────────────────

export type UserHabitPayload = {
  category?: number | null;
  activity_name?: string;
  description?: string;
  duration?: number | null;
  is_active?: boolean;
  schedule_time?: string | null;
};

export const editUserHabit = (id: number, data: Partial<UserHabitPayload>) =>
  requestJson(`/api/habits/${id}/edit/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);

export const deleteUserHabit = (id: number) =>
  requestJson(`/api/habits/${id}/delete/`, { method: "DELETE" });

export type AdminHabit = {
  id: number;
  user: number;
  user_username?: string;
  category: number;
  category_name?: string;
  activity_name: string;
  description?: string;
  duration?: number | null;
  is_active: boolean;
  schedule_time?: string | null;
  created_at: string;
};

// ── Habit Templates ──────────────────────────────────────────

export type HabitTemplate = {
  id: number;
  category: number;
  category_name?: string;
  activity_name: string;
  description: string;
  duration: number;
  is_active: boolean;
  schedule_time?: string | null;
  created_at: string;
};

export type HabitTemplatePayload = {
  category: number;
  activity_name: string;
  description: string;
  duration: number;
  is_active: boolean;
  schedule_time?: string | null;
};

export const listHabitTemplates = (query?: { category?: number; search?: string }) =>
  requestJson("/api/admin/habit-templates/", { query }).then(extractData);

export const createHabitTemplate = (data: HabitTemplatePayload) =>
  requestJson("/api/admin/habit-templates/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);

export const updateHabitTemplate = (id: number, data: Partial<HabitTemplatePayload>) =>
  requestJson(`/api/admin/habit-templates/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);

export const deleteHabitTemplate = (id: number) =>
  requestJson(`/api/admin/habit-templates/${id}/`, { method: "DELETE" });