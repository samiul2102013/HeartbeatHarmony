import { requestJson, uploadJsonWithProgress } from "../core/client";
 
export type MaterialQuery = {
  topic?: number;
  material_type?: "pdf" | "text" | "video";
  is_active?: boolean;
  search?: string;
  page?: number;
};
 
export const listMaterials = (query?: MaterialQuery) =>
  requestJson("/api/admin/study/materials/", { query });
 
export const getMaterial = (id: number) =>
  requestJson(`/api/admin/study/materials/${id}/`);
 
export const createMaterial = (data: FormData | Record<string, any>): Promise<AdminMaterial> => {
  const isFormData = data instanceof FormData;
  return requestJson("/api/admin/study/materials/", {
    method: "POST",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  });
};
 
export const updateMaterial = (id: number, data: FormData | Record<string, any>) => {
  const isFormData = data instanceof FormData;
  return requestJson(`/api/admin/study/materials/${id}/`, {
    method: "PATCH",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  });
};
 
export const deleteMaterial = (id: number) =>
  requestJson(`/api/admin/study/materials/${id}/`, { method: "DELETE" });

export const createMaterialWithProgress = (
  data: FormData,
  onProgress?: (percent: number) => void
): Promise<AdminMaterial> =>
  uploadJsonWithProgress<AdminMaterial>("/api/admin/study/materials/", data, onProgress, "POST");

export const updateMaterialWithProgress = (
  id: number,
  data: FormData,
  onProgress?: (percent: number) => void
) =>
  uploadJsonWithProgress(`/api/admin/study/materials/${id}/`, data, onProgress, "PATCH");

export type AdminMaterial = {
  id: number;
  topic: number;
  topic_title?: string;
  title: string;
  material_type: "pdf" | "text" | "video";
  is_active: boolean;
  created_at: string;
  pdf?: string | null;
  file?: string | null;
};

export type AdminCategory = {
  id: number;
  name: string;
};
 