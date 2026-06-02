import { requestJson } from "../core/client";

const extractData = (res: any) => res?.data ?? res;

export type HabitMaterialQuery = {
  habit?: number;
  material_type?: "pdf" | "text" | "video" | "audio";
  is_active?: boolean;
  search?: string;
};

export type AdminHabitMaterial = {
  id: number;
  habit: number;
  habit_title?: string;
  habit_user?: string;
  title: string;
  description?: string;
  material_type: "pdf" | "text" | "video" | "audio";
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  pdf?: string | null;
  file?: string | null;
  audio?: string | null;
  video_url?: string | null;
  content?: string | null;
};

export const listHabitMaterials = (query?: HabitMaterialQuery) =>
  requestJson("/api/admin/habit-materials/", { query }).then(extractData);

export const createHabitMaterial = (data: FormData | Record<string, any>) => {
  const isFormData = data instanceof FormData;
  return requestJson("/api/admin/habit-materials/", {
    method: "POST",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  }).then(extractData);
};

export const updateHabitMaterial = (id: number, data: FormData | Record<string, any>) => {
  const isFormData = data instanceof FormData;
  return requestJson(`/api/admin/habit-materials/${id}/`, {
    method: "PATCH",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  }).then(extractData);
};

export const editHabitMaterial = (id: number, data: FormData | Record<string, any>) => {
  const isFormData = data instanceof FormData;
  return requestJson(`/api/admin/habit-materials/${id}/edit/`, {
    method: "PATCH",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  }).then(extractData);
};

export const deleteHabitMaterial = (id: number) =>
  requestJson(`/api/admin/habit-materials/${id}/`, { method: "DELETE" });

export const removeHabitMaterial = (id: number) =>
  requestJson(`/api/admin/habit-materials/${id}/delete/`, { method: "DELETE" });