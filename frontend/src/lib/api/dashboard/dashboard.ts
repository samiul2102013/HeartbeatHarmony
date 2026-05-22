import { requestJson } from "../core/client";
 
export const getDashboardStats = () =>
  requestJson("/api/admin/dashboard/");