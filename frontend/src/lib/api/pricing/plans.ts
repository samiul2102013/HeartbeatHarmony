import { requestJson } from "../core/client";
 
export type PlanPayload = {
  name: string;
  slug: string;
  description?: string;
  price: string;           // e.g. "9.99"
  duration: "monthly" | "yearly" | "lifetime";
  is_active: boolean;
  is_popular: boolean;
};
 
const extractData = (res: any) => res?.data ?? res;

export const listPlans = (): Promise<PricingPlan[]> =>
  requestJson("/api/admin/pricing/plans/").then(extractData);
 
export const getPlan = (id: number): Promise<PricingPlan> =>
  requestJson(`/api/admin/pricing/plans/${id}/`).then(extractData);
 
export const createPlan = (data: PlanPayload): Promise<PricingPlan> =>
  requestJson("/api/admin/pricing/plans/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const updatePlan = (id: number, data: Partial<PlanPayload>): Promise<PricingPlan> =>
  requestJson(`/api/admin/pricing/plans/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const deletePlan = (id: number) =>
  requestJson(`/api/admin/pricing/plans/${id}/`, { method: "DELETE" });

export type PlanFeature = {
  id: number;
  title: string;
  is_included: boolean;
};

export type PricingPlan = {
  id: number;
  name: string;
  slug: string;
  description?: string;
  price: string;
  duration: "monthly" | "yearly" | "lifetime";
  is_active: boolean;
  is_popular: boolean;
  features?: PlanFeature[];
};