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