import { requestJson } from "../core/client";
 
export type CategoryPayload = {
  name: string;
  icon: string;
  is_active: boolean;
};

export type Category = CategoryPayload & {
  name: string;
  icon: string;
  is_active: boolean;
};

export type AdminCategory = {
  id: number;
  name: string;
  icon: string;
  is_active: boolean;
 };

export type CategoryListResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminCategory[];
};

export const listCategories = () =>
  requestJson<CategoryListResponse>("/api/admin/categories/");
 
export const getCategory = (id: number) =>
  requestJson<AdminCategory>(`/api/admin/categories/${id}/`);
 
export const createCategory = (data: CategoryPayload) =>
  requestJson<AdminCategory>("/api/admin/categories/", {
    method: "POST",
    body: JSON.stringify(data),
  });
 
export const updateCategory = (id: number, data: Partial<CategoryPayload>) =>
  requestJson<AdminCategory>(`/api/admin/categories/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
 
export const deleteCategory = (id: number) =>
  requestJson(`/api/admin/categories/${id}/`, { method: "DELETE" });