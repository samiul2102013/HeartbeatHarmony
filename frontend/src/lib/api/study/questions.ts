import { requestJson } from "../core/client";
 
export type QuestionPayload = {
  topic: number;
  quiz: number;
  text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_option: "A" | "B" | "C" | "D";
  order: number;
};
 
const extractData = (res: any) => res?.data ?? res;

export const listQuestions = (query?: { quiz?: number }) =>
  requestJson("/api/admin/study/questions/", { query });
 
export const getQuestion = (id: number) =>
  requestJson(`/api/admin/study/questions/${id}/`).then(extractData);
 
export const createQuestion = (data: QuestionPayload) =>
  requestJson("/api/admin/study/questions/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const updateQuestion = (id: number, data: Partial<QuestionPayload>) =>
  requestJson(`/api/admin/study/questions/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const deleteQuestion = (id: number) =>
  requestJson(`/api/admin/study/questions/${id}/`, { method: "DELETE" });