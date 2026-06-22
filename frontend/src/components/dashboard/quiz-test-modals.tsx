"use client";

import { useMemo, useState } from "react";
import { Plus, ChevronDown, ChevronUp } from "lucide-react";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";

export type QuizOption = {
	id: number;
	text: string;
	isCorrect: boolean;
};

export type QuizQuestion = {
	id: number;
	topic: string;
	topicId: number;
	title: string;
	options: QuizOption[];
};

export type TopicOption = {
	id: number;
	title: string;
};

export type QuizPayload = {
	title: string;
	type: string;
	topicId?: number;
	questions: QuizQuestion[];
};

type QuizScoreRow = {
	id: number;
	user: string;
	score: number;
};

interface CreateQuizModalProps {
	open: boolean;
	onOpenChange: (v: boolean) => void;
	topics?: TopicOption[];
	onSubmit?: (data: QuizPayload) => void;
}

interface ViewQuizDetailsModalProps {
	open: boolean;
	onOpenChange: (v: boolean) => void;
	quizTitle: string;
	questions: QuizQuestion[];
	onUpdateQuestion?: (id: number, payload: { text: string; option_a: string; option_b: string; option_c: string; option_d: string; correct_option: "A" | "B" | "C" | "D" }) => void | Promise<void>;
}

interface QuizScoreModalProps {
	open: boolean;
	onOpenChange: (v: boolean) => void;
	quizTitle: string;
	scores?: QuizScoreRow[];
}

function ModalFooter({
	onCancel,
	confirmLabel,
	onConfirm,
	confirmVariant = "solid",
}: {
	onCancel: () => void;
	confirmLabel: string;
	onConfirm?: () => void;
	confirmVariant?: "solid" | "outline";
}) {
	return (
		<div className="mt-6 flex gap-3">
			<Button type="button" variant="outline" className="flex-1 h-11 text-sm font-medium" onClick={onCancel}>
				Cancel
			</Button>
			<Button
				type="button"
				variant={confirmVariant === "outline" ? "outline" : "default"}
				className="flex-1 h-11 text-sm font-medium"
				style={
					confirmVariant === "solid"
						? { backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }
						: undefined
				}
				onClick={onConfirm}
			>
				{confirmLabel}
			</Button>
		</div>
	);
}

function alphabetLabel(index: number) {
	return String.fromCharCode(97 + index);
}

export function CreateQuizModal({ open, onOpenChange, topics = [], onSubmit }: CreateQuizModalProps) {
	const [step, setStep] = useState<1 | 2>(1);
	const [quizTitle, setQuizTitle] = useState("");
	const [topicId, setTopicId] = useState<string>("");
	const [questionTitle, setQuestionTitle] = useState("");
	const [optionText, setOptionText] = useState("");
	const [markAsCorrect, setMarkAsCorrect] = useState(false);
	const [currentOptions, setCurrentOptions] = useState<QuizOption[]>([]);
	const [questions, setQuestions] = useState<QuizQuestion[]>([]);
	const [editingOptionId, setEditingOptionId] = useState<number | null>(null);
	const [draftOptionText, setDraftOptionText] = useState("");
	const [draftOptionCorrect, setDraftOptionCorrect] = useState(false);
	const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);
	const [draftQuestionTitle, setDraftQuestionTitle] = useState("");
	const [draftQuestionOptions, setDraftQuestionOptions] = useState<QuizOption[]>([]);
	const [draftCorrectIndex, setDraftCorrectIndex] = useState(0);

	const reset = () => {
		setStep(1);
		setQuizTitle("");
		setTopicId(topics[0]?.id ? String(topics[0].id) : "");
		setQuestionTitle("");
		setOptionText("");
		setMarkAsCorrect(false);
		setCurrentOptions([]);
		setQuestions([]);
		setEditingOptionId(null);
		setDraftOptionText("");
		setDraftOptionCorrect(false);
		setEditingQuestionId(null);
		setDraftQuestionTitle("");
		setDraftQuestionOptions([]);
		setDraftCorrectIndex(0);
	};

	const addOption = () => {
		const trimmed = optionText.trim();
		if (!trimmed) return;
		setCurrentOptions((prev) => [
			...prev,
			{ id: Date.now(), text: trimmed, isCorrect: markAsCorrect },
		]);
		setOptionText("");
		setMarkAsCorrect(false);
	};

	const startEditOption = (option: QuizOption) => {
		setEditingOptionId(option.id);
		setDraftOptionText(option.text);
		setDraftOptionCorrect(option.isCorrect);
	};

	const cancelEditOption = () => {
		setEditingOptionId(null);
		setDraftOptionText("");
		setDraftOptionCorrect(false);
	};

	const saveEditedOption = (optionId: number) => {
		const nextText = draftOptionText.trim();
		if (!nextText) return;

		setCurrentOptions((prev) =>
			prev.map((option) =>
				option.id === optionId
					? { ...option, text: nextText, isCorrect: draftOptionCorrect }
					: option
			)
		);
		cancelEditOption();
	};

	const deleteOption = (optionId: number) => {
		setCurrentOptions((prev) => prev.filter((option) => option.id !== optionId));
		if (editingOptionId === optionId) {
			cancelEditOption();
		}
	};

	const selectedTopic = topics.find((t) => String(t.id) === topicId);

	const addQuestion = () => {
		const title = questionTitle.trim();
		if (!title || currentOptions.length < 2) return;
		const hasCorrect = currentOptions.some((option) => option.isCorrect);
		if (!hasCorrect) return;

		setQuestions((prev) => [
			...prev,
			{
				id: Date.now(),
				topic: selectedTopic?.title ?? "",
				topicId: selectedTopic?.id ?? Number(topicId),
				title,
				options: currentOptions,
			},
		]);
		setQuestionTitle("");
		setCurrentOptions([]);
	};

	const startEditQuestion = (question: QuizQuestion) => {
		setEditingQuestionId(question.id);
		setDraftQuestionTitle(question.title);
		setDraftQuestionOptions(question.options.map((option) => ({ ...option })));
		setDraftCorrectIndex(question.options.findIndex((option) => option.isCorrect));
	};

	const cancelEditQuestion = () => {
		setEditingQuestionId(null);
		setDraftQuestionTitle("");
		setDraftQuestionOptions([]);
		setDraftCorrectIndex(0);
	};

	const saveEditedQuestion = (questionId: number) => {
		const title = draftQuestionTitle.trim();
		if (!title || draftQuestionOptions.length < 2) return;

		const nextOptions = draftQuestionOptions.map((option, index) => ({
			...option,
			text: option.text.trim(),
			isCorrect: index === draftCorrectIndex,
		}));

		if (nextOptions.some((option) => !option.text)) return;

		setQuestions((prev) =>
			prev.map((question) =>
				question.id === questionId
					? {
						...question,
						title,
						options: nextOptions,
					}
					: question
			)
		);
		cancelEditQuestion();
	};
	const submitQuiz = () => {
		if (!quizTitle.trim() || questions.length === 0) return;
		onSubmit?.({
			title: quizTitle.trim(),
			type: "Question Set",
			topicId: selectedTopic?.id,
			questions,
		});
		reset();
		onOpenChange(false);
	};

	const canProceed = quizTitle.trim().length > 0;
	const canAddQuestion = questionTitle.trim().length > 0 && currentOptions.length >= 2;

	return (
		<Dialog
			open={open}
			onOpenChange={(v) => {
				if (!v) reset();
				onOpenChange(v);
			}}
		>
			<DialogContent className="sm:max-w-3xl rounded-2xl p-6 gap-0">
				<DialogHeader className="mb-5">
					<DialogTitle className="text-4xl font-bold text-foreground">Create Quiz</DialogTitle>
					<DialogDescription className="text-sm text-muted-foreground">
						Drag and drop your files here
					</DialogDescription>
				</DialogHeader>

				{step === 1 ? (
					<div>
						<div className="grid grid-cols-1 gap-4">
							<div className="space-y-1.5">
								<Label className="px-0 text-sm font-semibold">Online Test Title</Label>
								<Input
									placeholder="Enter title"
									value={quizTitle}
									onChange={(e) => setQuizTitle(e.target.value)}
									className="h-11"
								/>
							</div>
						</div>

						<ModalFooter
							onCancel={() => {
								reset();
								onOpenChange(false);
							}}
							confirmLabel="Next"
							onConfirm={() => {
								if (canProceed) setStep(2);
							}}
						/>
					</div>
				) : (
					<div className="space-y-5 max-h-[65vh] overflow-y-auto pr-1">
						<div className="space-y-1.5">
							<Label className="px-0 text-sm font-semibold">Subject Name</Label>
							  <Select value={topicId} onValueChange={(value) => setTopicId(value ?? "") }>
								<SelectTrigger className="h-11 w-full">
									<SelectValue placeholder="Select subject">{topics.find((t) => String(t.id) === topicId)?.title || "Select subject"}</SelectValue>
								</SelectTrigger>
								<SelectContent>
									{topics.map((t) => (
										<SelectItem key={t.id} value={String(t.id)}>{t.title}</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>

						<div className="space-y-1.5">
							<Label className="px-0 text-sm font-semibold">Question</Label>
							<Input
								placeholder="Enter question title"
								value={questionTitle}
								onChange={(e) => setQuestionTitle(e.target.value)}
								className="h-11"
							/>
						</div>

						<div className="space-y-1.5">
							<Label className="px-0 text-sm font-semibold">Option</Label>
							<Input
								placeholder="Enter option"
								value={optionText}
								onChange={(e) => setOptionText(e.target.value)}
								className="h-11"
							/>
							<div className="flex items-center justify-between pt-1">
								<label className="inline-flex items-center gap-2 text-sm text-foreground">
									<Checkbox
										checked={markAsCorrect}
										onCheckedChange={(checked) => setMarkAsCorrect(Boolean(checked))}
									/>
									Marked as correct answer
								</label>
								<Button
									type="button"
									variant="secondary"
									className="h-9 text-sm"
									style={{ color: "var(--primary)", backgroundColor: "rgba(209,61,61,0.08)" }}
									onClick={addOption}
								>
									<Plus className="h-4 w-4" /> Add Another option
								</Button>
							</div>
						</div>

						{currentOptions.length > 0 && (
							<div className="rounded-lg border border-border p-3 space-y-2">
								<p className="text-sm font-semibold">Current options</p>
								{currentOptions.map((option, idx) => {
									const isEditing = editingOptionId === option.id;
									return (
										<div key={option.id} className="space-y-2 rounded-md border border-border/60 bg-background p-3">
											{!isEditing ? (
												<div className="flex items-start justify-between gap-3">
													<p className="text-sm text-muted-foreground">
														{idx + 1}. {option.text} {option.isCorrect ? "(Correct)" : ""}
													</p>
													<div className="flex shrink-0 gap-2">
														<Button type="button" variant="ghost" className="h-7 px-2 text-xs" onClick={() => startEditOption(option)}>
															Edit
														</Button>
														<Button type="button" variant="ghost" className="h-7 px-2 text-xs text-destructive" onClick={() => deleteOption(option.id)}>
															Delete
														</Button>
													</div>
												</div>
											) : (
												<div className="space-y-3">
													<Input value={draftOptionText} onChange={(e) => setDraftOptionText(e.target.value)} className="h-10 text-sm" />
													<label className="inline-flex items-center gap-2 text-xs text-foreground">
														<Checkbox checked={draftOptionCorrect} onCheckedChange={(checked) => setDraftOptionCorrect(Boolean(checked))} />
														Marked as correct answer
													</label>
													<div className="flex gap-2">
														<Button type="button" variant="outline" className="h-8 text-xs" onClick={cancelEditOption}>Cancel</Button>
														<Button type="button" className="h-8 text-xs" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => saveEditedOption(option.id)}>Save</Button>
													</div>
												</div>
											)}
										</div>
									);
								})}
							</div>
						)}

						<div className="flex justify-end">
							<Button
								type="button"
								className="h-9 text-sm"
								style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
								onClick={addQuestion}
								disabled={!canAddQuestion}
							>
								Add Question
							</Button>
						</div>

						{questions.length > 0 && (
							<div className="rounded-lg border border-border p-4 space-y-4 max-h-64 overflow-auto">
								<p className="text-base font-semibold">Question List</p>
								{questions.map((question, qIdx) => {
									const correctIndex = question.options.findIndex((opt) => opt.isCorrect);
									const isEditing = editingQuestionId === question.id;
									return (
										<div key={question.id} className="space-y-2">
											{!isEditing ? (
												<>
													<div className="flex items-start justify-between gap-3">
														<p className="text-sm font-medium">
															{qIdx + 1}. {question.title}
														</p>
														<Button type="button" variant="ghost" className="h-8 px-2 text-xs" onClick={() => startEditQuestion(question)}>
															Edit
														</Button>
													</div>
													{question.options.map((option) => (
														<p key={option.id} className="text-xs text-muted-foreground">○ {option.text}</p>
													))}
													<p className="text-sm font-medium">
														Subject: {question.topic} &nbsp; Correct Answer: {correctIndex >= 0 ? alphabetLabel(correctIndex) : "-"}
													</p>
												</>
											) : (
												<div className="space-y-3 rounded-md border border-border bg-muted/30 p-3">
													<div className="space-y-1.5">
														<Label className="text-xs font-semibold">Question</Label>
														<Input value={draftQuestionTitle} onChange={(e) => setDraftQuestionTitle(e.target.value)} className="h-10 text-sm" />
													</div>

													<div className="space-y-2">
														<Label className="text-xs font-semibold">Options</Label>
														{draftQuestionOptions.map((option, optIdx) => (
															<div key={option.id} className="flex items-center gap-2">
																<Input
																	value={option.text}
																	onChange={(e) => {
																		const next = [...draftQuestionOptions];
																		next[optIdx] = { ...next[optIdx], text: e.target.value };
																		setDraftQuestionOptions(next);
																	}}
																	className="h-10 text-sm flex-1"
																/>
																<label className="inline-flex items-center gap-1.5 text-xs text-foreground shrink-0">
																	<input
																		type="radio"
																		name={`edit-correct-${question.id}`}
																		checked={draftCorrectIndex === optIdx}
																		onChange={() => setDraftCorrectIndex(optIdx)}
																		className="h-4 w-4"
																	/>
																	Correct
																</label>
															</div>
														))}
													</div>

													<div className="flex gap-2 pt-1">
														<Button type="button" variant="outline" className="h-8 text-xs" onClick={cancelEditQuestion}>
															Cancel
														</Button>
														<Button
															type="button"
															className="h-8 text-xs"
															style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
															onClick={() => saveEditedQuestion(question.id)}
														>
															Save Changes
														</Button>
													</div>
												</div>
										)}
									</div>
								);
								})}
							</div>
						)}

						<ModalFooter
							onCancel={() => {
								reset();
								onOpenChange(false);
							}}
							confirmLabel="Save"
							onConfirm={submitQuiz}
						/>
					</div>
				)}
			</DialogContent>
		</Dialog>
	);
}

export function ViewQuizDetailsModal({
	open,
	onOpenChange,
	quizTitle,
	questions,
	onUpdateQuestion,
}: ViewQuizDetailsModalProps) {
	const [openQuestionId, setOpenQuestionId] = useState<number | null>(questions[0]?.id ?? null);
	const [editingId, setEditingId] = useState<number | null>(null);
	const [draftTitle, setDraftTitle] = useState("");
	const [draftOptions, setDraftOptions] = useState<string[]>(["", "", "", ""]);
	const [draftCorrectIndex, setDraftCorrectIndex] = useState(0);
	const [saving, setSaving] = useState(false);

	const startEdit = (question: QuizQuestion) => {
		setEditingId(question.id);
		setDraftTitle(question.title);
		const opts = question.options.map((o) => o.text);
		while (opts.length < 4) opts.push("");
		setDraftOptions(opts.slice(0, 4));
		setDraftCorrectIndex(question.options.findIndex((o) => o.isCorrect) ?? 0);
		setOpenQuestionId(question.id);
	};

	const cancelEdit = () => {
		setEditingId(null);
		setDraftTitle("");
		setDraftOptions(["", "", "", ""]);
		setDraftCorrectIndex(0);
	};

	const saveEdit = async (question: QuizQuestion) => {
		if (!onUpdateQuestion) return;
		setSaving(true);
		try {
			await onUpdateQuestion(question.id, {
				text: draftTitle.trim(),
				option_a: draftOptions[0] ?? "",
				option_b: draftOptions[1] ?? "",
				option_c: draftOptions[2] ?? "",
				option_d: draftOptions[3] ?? "",
				correct_option: (["A", "B", "C", "D"] as const)[draftCorrectIndex] ?? "A",
			});
			setEditingId(null);
		} finally {
			setSaving(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-3xl rounded-2xl p-6 gap-0">
				<DialogHeader className="mb-5 shrink-0">
					<DialogTitle className="text-3xl font-bold text-foreground">Quiz Details</DialogTitle>
					<DialogDescription className="text-sm text-muted-foreground">
						{quizTitle}
					</DialogDescription>
				</DialogHeader>

				<div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1">
					<div className="flex items-center justify-between">
						<p className="text-2xl font-semibold">Question List</p>
					</div>

					<div className="max-h-96 overflow-auto pr-1 space-y-3">
						{questions.map((question, idx) => {
							const isOpen = openQuestionId === question.id;
							const isEditing = editingId === question.id;
							const correctIndex = question.options.findIndex((opt) => opt.isCorrect);
							return (
								<div key={question.id} className="rounded-lg border border-border p-3">
									<div
										role="button"
										tabIndex={0}
										className="w-full flex items-center justify-between gap-3 text-left cursor-pointer"
										onClick={() => setOpenQuestionId(isOpen ? null : question.id)}
									>
										<span className="text-sm sm:text-base font-semibold">
											{idx + 1}. {question.title}
										</span>
										<div className="flex items-center gap-2">
											{!isEditing && (
												<Button
													type="button"
													variant="ghost"
													className="h-7 px-2 text-xs"
													onClick={(e) => { e.stopPropagation(); startEdit(question); }}
												>
													Edit
												</Button>
											)}
											{isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
										</div>
									</div>

									{isOpen && !isEditing && (
										<div className="pt-3 space-y-2">
											{question.options.map((option) => (
												<p key={option.id} className="text-xs sm:text-sm text-muted-foreground">○ {option.text}</p>
											))}
											<p className="text-sm font-medium">
												Subject: {question.topic} &nbsp; Correct Answer: {correctIndex >= 0 ? alphabetLabel(correctIndex) : "-"}
											</p>
										</div>
									)}

									{isOpen && isEditing && (
										<div className="pt-3 space-y-3">
											<div className="space-y-1">
												<Label className="text-xs font-semibold">Question</Label>
												<Input
													value={draftTitle}
													onChange={(e) => setDraftTitle(e.target.value)}
													className="h-10 text-sm"
												/>
											</div>
											{draftOptions.map((opt, optIdx) => (
												<div key={optIdx} className="flex items-center gap-2">
													<Input
														value={opt}
														onChange={(e) => {
															const next = [...draftOptions];
															next[optIdx] = e.target.value;
															setDraftOptions(next);
														}}
														placeholder={`Option ${alphabetLabel(optIdx).toUpperCase()}`}
														className="h-10 text-sm flex-1"
													/>
													<label className="inline-flex items-center gap-1.5 text-xs text-foreground shrink-0">
														<input
															type="radio"
															name={`correct-${question.id}`}
															checked={draftCorrectIndex === optIdx}
															onChange={() => setDraftCorrectIndex(optIdx)}
															className="h-4 w-4"
														/>
														Correct
													</label>
												</div>
											))}
											<div className="flex gap-2 pt-1">
												<Button
													type="button"
													variant="outline"
													className="h-8 text-xs"
													onClick={cancelEdit}
												>
													Cancel
												</Button>
												<Button
													type="button"
													className="h-8 text-xs"
													style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
													onClick={() => void saveEdit(question)}
													disabled={saving}
												>
													{saving ? "Saving..." : "Save"}
												</Button>
											</div>
										</div>
									)}
								</div>
							);
						})}
					</div>

					<p className="text-xs text-muted-foreground">Quiz: {quizTitle}</p>
				</div>

				<ModalFooter onCancel={() => onOpenChange(false)} confirmLabel="Close" onConfirm={() => onOpenChange(false)} />
			</DialogContent>
		</Dialog>
	);
}

export function QuizScoreModal({ open, onOpenChange, quizTitle, scores }: QuizScoreModalProps) {
	const rows = scores ?? [];
	const avg = Math.round(rows.reduce((acc, row) => acc + row.score, 0) / rows.length);

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-xl rounded-2xl p-6 gap-0">
				<DialogHeader className="mb-5">
					<DialogTitle className="text-3xl font-bold text-foreground">Quiz Score</DialogTitle>
					<DialogDescription className="text-sm text-muted-foreground">
						{quizTitle}
					</DialogDescription>
				</DialogHeader>

				<div className="space-y-3">
					<div className="rounded-lg border border-border p-3 bg-muted/20">
						<p className="text-sm text-muted-foreground">Average Score</p>
						<p className="text-2xl font-semibold text-foreground">{avg}%</p>
					</div>

					<div className="rounded-lg border border-border overflow-hidden">
						<div className="grid grid-cols-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground px-4 py-2" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
							<p>User</p>
							<p className="text-right">Score</p>
						</div>
						{rows.map((row) => (
							<div key={row.id} className="grid grid-cols-2 px-4 py-2 border-t border-border">
								<p className="text-sm font-medium text-foreground">{row.user}</p>
								<p className="text-sm text-right font-semibold" style={{ color: row.score >= 80 ? "#16a34a" : row.score >= 60 ? "#ca8a04" : "#dc2626" }}>
									{row.score}%
								</p>
							</div>
						))}
					</div>
				</div>

				<ModalFooter onCancel={() => onOpenChange(false)} confirmLabel="Done" onConfirm={() => onOpenChange(false)} />
			</DialogContent>
		</Dialog>
	);
}
