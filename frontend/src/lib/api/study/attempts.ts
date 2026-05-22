import { requestJson } from "../core/client";
 
export type AttemptQuery = {
  quiz?: number;
  user?: number;
  search?: string;
  page?: number;
};

export type QuizAttempt = {
  id: number;
  user_username: string;
  score: number;
  total_questions: number;
  score_percentage: number;
  completed_at: string;
};
 
const extractData = (res: any) => res?.data ?? res;

export const listAttempts = (query?: AttemptQuery): Promise<QuizAttempt[]> =>
  requestJson("/api/admin/study/attempts/", { query }).then(extractData);