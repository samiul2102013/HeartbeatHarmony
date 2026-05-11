import { requestJson } from "../core/client";
 
export type QuizQuery = {
  topic?: number;
  is_active?: boolean;
  search?: string;
  page?: number;
};
 
export type QuizPayload = {
  topic: number;
  title: string;
  description?: string;
  is_active: boolean;
};
 
const extractData = (res: any) => res?.data ?? res;

export const listQuizzes = (query?: QuizQuery) =>
  requestJson("/api/admin/study/quizzes/", { query }).then(extractData);
 
export const getQuiz = (id: number): Promise<StudyQuiz> =>
  requestJson(`/api/admin/study/quizzes/${id}/`).then(extractData);
 
export const createQuiz = (data: QuizPayload): Promise<StudyQuiz> =>
  requestJson("/api/admin/study/quizzes/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const updateQuiz = (id: number, data: Partial<QuizPayload>): Promise<StudyQuiz> =>
  requestJson(`/api/admin/study/quizzes/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  }).then(extractData);
 
export const deleteQuiz = (id: number) =>
  requestJson(`/api/admin/study/quizzes/${id}/`, { method: "DELETE" });

export type StudyQuiz = {
  id: number;
  topic: number;
  topic_title?: string;
  title: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  questions?: StudyQuestion[];
};

export type StudyQuestion = {
  id: number;
  topic: number;
  topic_id?: number;
  topic_title?: string;
  quiz: number;
  text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_option: "A" | "B" | "C" | "D";
  order: number;
};