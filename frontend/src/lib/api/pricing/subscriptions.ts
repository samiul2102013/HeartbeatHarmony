import { requestJson } from "../core/client";
 
export type SubscriptionQuery = {
  status?: "active" | "cancelled" | "expired";
  plan?: number;
  search?: string;
  page?: number;
};
 
export const listSubscriptions = (query?: SubscriptionQuery) =>
  requestJson("/api/admin/pricing/subscriptions/", { query });
 
export const getSubscription = (id: number) =>
  requestJson(`/api/admin/pricing/subscriptions/${id}/`);
 
export const updateSubscription = (
  id: number,
  data: { status: "active" | "cancelled" | "expired" }
) =>
  requestJson(`/api/admin/pricing/subscriptions/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });