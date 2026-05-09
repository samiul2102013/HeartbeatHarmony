import { requestJson } from "../core/client";
 
export const listMessages = () =>
  requestJson("/api/admin/community/messages/");
 
export const deleteMessage = (id: number) =>
  requestJson(`/api/admin/community/messages/${id}/`, { method: "DELETE" });