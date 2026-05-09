import { requestJson } from "../core/client";
 
export type MoodPayload = {
  name: string;
  emoji: string;
  score: number;       // 1-10
  is_active: boolean;
};

export type AdminMood = {
  id: number;
  name: string;
  emoji: string;
  svg: string | null;
  score: number;
  is_active: boolean;
};

export type MoodListResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminMood[];
}
export const listMoods = () =>
  requestJson<MoodListResponse>("/api/admin/moods/");
 
export const getMood = (id: number) =>
  requestJson<AdminMood>(`/api/admin/moods/${id}/`);
 
export const createMood = (data: MoodPayload | FormData) =>
  requestJson<AdminMood>("/api/admin/moods/", {
    method: "POST",
    body: data instanceof FormData ? data : JSON.stringify(data),
  });
 
export const updateMood = (id: number, data: Partial<MoodPayload> | FormData) =>
  requestJson<AdminMood>(`/api/admin/moods/${id}/`, {
    method: "PATCH",
    body: data instanceof FormData ? data : JSON.stringify(data),
  });
 
export const deleteMood = (id: number) =>
  requestJson<AdminMood>(`/api/admin/moods/${id}/`, { method: "DELETE" });