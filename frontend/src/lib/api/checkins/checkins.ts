import { requestJson } from "../core/client";
 
export type CheckinQuery = {
  user?: number;
  mood?: number;
  ordering?: "created_at" | "-created_at" | "heart_balance_score" | "-heart_balance_score";
  search?: string;
  page?: number;
};
 
export const listCheckins = (query?: CheckinQuery) =>
  requestJson("/api/admin/checkins/", { query });
 
export const getCheckin = (id: number) =>
  requestJson(`/api/admin/checkins/${id}/`);
 
export const deleteCheckin = (id: number) =>
  requestJson(`/api/admin/checkins/${id}/`, { method: "DELETE" });

export type AdminCheckIn = {
  id: number;
  user_username: string;
  mood_name: string;
  created_at: string;
  heart_balance_score: number;
};
 