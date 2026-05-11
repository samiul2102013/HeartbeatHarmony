import { requestJson } from "../core/client";

const extractData = (res: any) => res?.data ?? res;
 
export const listTopics = () =>
  requestJson("/api/admin/study/topics/").then(extractData);
 
export const getTopic = (id: number) =>
  requestJson(`/api/admin/study/topics/${id}/`).then(extractData);
 
export const createTopic = (data: FormData | Record<string, any>) => {
  const isFormData = data instanceof FormData;
  return requestJson("/api/admin/study/topics/", {
    method: "POST",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  }).then(extractData);
};
 
export const updateTopic = (id: number, data: FormData | Record<string, any>) => {
  const isFormData = data instanceof FormData;
  return requestJson(`/api/admin/study/topics/${id}/`, {
    method: "PATCH",
    body: isFormData ? data : JSON.stringify(data),
    skipContentType: isFormData,
  }).then(extractData);
};
 
export const deleteTopic = (id: number) =>
  requestJson(`/api/admin/study/topics/${id}/`, { method: "DELETE" });

export type StudyTopic = {
  id: number;
  title: string;
  name?: string;
  description?: string;
  last_correct_answers?: number;
  last_total_questions?: number;
  last_attempted_score?: number;
};