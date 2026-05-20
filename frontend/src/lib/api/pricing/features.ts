import { requestJson } from "../core/client";
import type { PlanFeature } from "./plans";

export type FeaturePayload = {
  plan: number;
  title: string;
  is_included: boolean;
  order: number;
};

const extractData = (res: any) => res?.data ?? res;
 
export const listFeatures = (query?: { plan?: number }): Promise<PlanFeature[]> =>
  requestJson("/api/admin/pricing/features/", { query }).then(extractData);
 
export const createFeature = (data: FeaturePayload): Promise<PlanFeature> =>
  requestJson("/api/admin/pricing/features/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const updateFeature = (id: number, data: Partial<FeaturePayload>): Promise<PlanFeature> =>
  requestJson(`/api/admin/pricing/features/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const deleteFeature = (id: number): Promise<void> =>
  requestJson(`/api/admin/pricing/features/${id}/`, { method: "DELETE" });