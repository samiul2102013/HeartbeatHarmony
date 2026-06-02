"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
  CreateQuizModal,
  QuizPayload,
  QuizQuestion,
  QuizScoreModal,
  ViewQuizDetailsModal,
} from "@/components/dashboard/quiz-test-modals";
import type { TopicOption } from "@/components/dashboard/quiz-test-modals";
import {
  createQuestion,
  createQuiz,
  getQuiz,
  listAttempts,
  listQuizzes,
  listTopics,
  updateQuestion,
  updateQuiz,
  StudyQuiz,
  StudyQuestion,
  StudyTopic,
} from "@/lib/index";
import { Plus, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type QuizItem = {
  id: number;
  title: string;
  date: string;
  type: string;
  is_selected: boolean;
  questions: QuizQuestion[];
};

type QuizScoreRow = {
  id: number;
  user: string;
  score: number;
};

function toQuizQuestions(topicTitle: string, questions: StudyQuestion[] | undefined): QuizQuestion[] {
  return (questions ?? []).map((question, index) => ({
    id: question.id,
    topic: question.topic_title ?? topicTitle,
    topicId: question.topic_id ?? question.topic,
    title: question.text,
    options: [
      { id: question.id * 10 + 1, text: question.option_a, isCorrect: question.correct_option === "A" },
      { id: question.id * 10 + 2, text: question.option_b, isCorrect: question.correct_option === "B" },
      { id: question.id * 10 + 3, text: question.option_c, isCorrect: question.correct_option === "C" },
      { id: question.id * 10 + 4, text: question.option_d, isCorrect: question.correct_option === "D" },
    ],
  }));
}

function mapQuiz(quiz: StudyQuiz): QuizItem {
  return {
    id: quiz.id,
    title: quiz.title,
    date: new Date(quiz.created_at).toLocaleDateString("en-US", {
      month: "2-digit",
      day: "2-digit",
      year: "2-digit",
    }),
    type: quiz.topic_title ?? "Question Set",
    is_selected: !!quiz.is_selected,
    questions: toQuizQuestions(quiz.topic_title ?? quiz.title, quiz.questions),
  };
}

export default function QuizTestPage() {
  const [search, setSearch] = useState("");
  const [quizzes, setQuizzes] = useState<QuizItem[]>([]);
  const [topics, setTopics] = useState<StudyTopic[]>([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [detailsQuiz, setDetailsQuiz] = useState<QuizItem | null>(null);
  const [scoreQuiz, setScoreQuiz] = useState<QuizItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSelectQuiz = async (quizId: number) => {
    try {
      await updateQuiz(quizId, { is_selected: true });
      const quizzesData = await listQuizzes();
      setQuizzes((Array.isArray(quizzesData) ? quizzesData : []).map(mapQuiz));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to select quiz");
    }
  };

    useEffect(() => {
    let mounted = true;

    const loadQuizzes = async () => {
      try {
        setLoading(true);
        const [quizzesData, topicsData] = await Promise.all([listQuizzes(), listTopics()]);
        if (!mounted) return;
        setQuizzes((Array.isArray(quizzesData) ? quizzesData : []).map(mapQuiz));
        setTopics(Array.isArray(topicsData) ? topicsData : []);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load quizzes");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void loadQuizzes();

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(
    () => quizzes.filter((quiz) => (quiz.title || "").toLowerCase().includes(search.toLowerCase())),
    [quizzes, search]
  );

  const handleCreateQuiz = async (data: QuizPayload) => {
    const topicId = data.topicId ?? data.questions[0]?.topicId ?? topics[0]?.id;
    if (!topicId) {
      throw new Error("No study topic available for quiz creation");
    }

    const createdQuiz = await createQuiz({
      topic: topicId,
      title: data.title,
      description: "Question Set",
      is_active: true,
    });

    for (let index = 0; index < data.questions.length; index += 1) {
      const question = data.questions[index];
      const options = question.options.slice(0, 4);
      while (options.length < 4) {
        options.push({ id: Date.now() + options.length, text: "", isCorrect: false });
      }
      const correctIndex = options.findIndex((option) => option.isCorrect);
      const questionTopicId = question.topicId ?? topicId;
      await createQuestion({
        topic: questionTopicId,
        quiz: createdQuiz.id,
        text: question.title,
        option_a: options[0]?.text ?? "",
        option_b: options[1]?.text ?? "",
        option_c: options[2]?.text ?? "",
        option_d: options[3]?.text ?? "",
        correct_option: ["A", "B", "C", "D"][correctIndex >= 0 ? correctIndex : 0] as "A" | "B" | "C" | "D",
        order: index + 1,
      });
    }

    const refreshedQuiz = await getQuiz(createdQuiz.id);
    setQuizzes((prev) => [mapQuiz(refreshedQuiz), ...prev.filter((quiz) => quiz.id !== refreshedQuiz.id)]);
  };

  const openDetails = async (quiz: QuizItem) => {
    const fullQuiz = await getQuiz(quiz.id);
    setDetailsQuiz(mapQuiz(fullQuiz));
  };

  const handleUpdateQuestion = async (
    id: number,
    payload: { text: string; option_a: string; option_b: string; option_c: string; option_d: string; correct_option: "A" | "B" | "C" | "D" }
  ) => {
    await updateQuestion(id, payload);
    if (detailsQuiz) {
      const fullQuiz = await getQuiz(detailsQuiz.id);
      setDetailsQuiz(mapQuiz(fullQuiz));
    }
  };

  const [scoreRows, setScoreRows] = useState<QuizScoreRow[]>([]);

  const handleOpenScore = async (quiz: QuizItem) => {
    const attempts = await listAttempts({ quiz: quiz.id });
    setScoreRows(
      attempts.map((attempt) => ({
        id: attempt.id,
        user: attempt.user_username,
        score: Math.round(attempt.score_percentage),
      }))
    );
    setScoreQuiz(quiz);
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Quiz Test</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Create and manage quizzes with questions and track scores.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="h-9 pl-9 text-sm" />
        </div>
        <Button className="h-9 gap-1.5 text-sm font-medium" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" /> Create Quiz
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {loading ? (
          <div className="col-span-full rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">Loading quizzes...</div>
        ) : filtered.length === 0 ? (
          <div className="col-span-full rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">No quizzes found.</div>
        ) : (
          filtered.map((quiz) => (
            <Card key={quiz.id} className="rounded-xl border border-border shadow-sm">
              <CardContent className="space-y-4 p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-semibold text-foreground">{quiz.title}</h3>
                    <p className="mt-1 text-sm font-semibold text-foreground">{quiz.type}</p>
                  </div>
                  <p className="text-sm text-muted-foreground">{quiz.date}</p>
                </div>

                <div className="flex items-center gap-2">
                  <Button className="h-8 px-3 text-sm" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => void openDetails(quiz)}>
                    View Details
                  </Button>
                  <Button variant="outline" className="h-8 px-3 text-sm" style={{ color: "var(--primary)", borderColor: "rgba(209,61,61,0.35)" }} onClick={() => void handleOpenScore(quiz)}>
                    See Score
                  </Button>
                  {quiz.is_selected ? (
                    <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-900/50 ml-auto">
                      Active on Mobile
                    </span>
                  ) : (
                    <Button variant="ghost" className="h-8 px-3 text-sm text-muted-foreground hover:text-foreground ml-auto" onClick={() => void handleSelectQuiz(quiz.id)}>
                      Select this quiz
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <CreateQuizModal
        open={createOpen}
        onOpenChange={setCreateOpen}
        topics={topics.map((t) => ({ id: t.id, title: t.title || (t as any).name || "Untitled" }))}
        onSubmit={(data) => void handleCreateQuiz(data)}
      />

      <ViewQuizDetailsModal
        open={Boolean(detailsQuiz)}
        onOpenChange={(v) => {
          if (!v) setDetailsQuiz(null);
        }}
        quizTitle={detailsQuiz?.title ?? ""}
        questions={detailsQuiz?.questions ?? []}
        onUpdateQuestion={handleUpdateQuestion}
      />

      <QuizScoreModal
        open={Boolean(scoreQuiz)}
        onOpenChange={(v) => {
          if (!v) setScoreQuiz(null);
        }}
        quizTitle={scoreQuiz?.title ?? ""}
        scores={scoreRows}
      />
    </div>
  );
}
