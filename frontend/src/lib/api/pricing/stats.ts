import { requestJson } from "../core/client";
 
export const getPricingStats = () =>
  requestJson("/api/admin/pricing/stats/");