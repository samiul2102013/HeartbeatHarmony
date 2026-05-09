import { requestJson } from "../core/client";
 
export type FeaturePayload = {
  plan: number;
  title: string;
  is_included: boolean;
  order: number;
};
 
export const listFeatures = (query?: { plan?: number }) =>
  requestJson("/api/admin/pricing/features/", { query });
 
export const createFeature = (data: FeaturePayload) =>
  requestJson("/api/admin/pricing/features/", {
    method: "POST",
    body: JSON.stringify(data),
  });
 
export const updateFeature = (id: number, data: Partial<FeaturePayload>) =>
  requestJson(`/api/admin/pricing/features/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
 
export const deleteFeature = (id: number) =>
  requestJson(`/api/admin/pricing/features/${id}/`, { method: "DELETE" });