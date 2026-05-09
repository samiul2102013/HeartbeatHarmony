"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ModalError, ModalField, ModalFooter } from "./shared";

type MoodType = "Positive" | "Neutral" | "Negative";

type AddMoodModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  onSubmit?: (data: { name: string; type: MoodType; score: string }) => void | Promise<void>;
};

export function AddMoodModal({ open, onOpenChange, onSubmit }: AddMoodModalProps) {
  const [name, setName] = useState("");
  const [type, setType] = useState<MoodType>("Positive");
  const [score, setScore] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setName("");
    setType("Positive");
    setScore("");
    setError(null);
    setSaving(false);
  };

  const handleConfirm = async () => {
    const nextName = name.trim();
    if (!nextName) {
      setError("Mood name is required.");
      return;
    }

    if (score.trim() && Number.isNaN(Number(score))) {
      setError("Score must be a valid number.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({ name: nextName, type, score });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create mood.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Add New Mood</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Capture a mood with a score that matches your scoring rules.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Name">
            <Input placeholder="Enter name" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
          </ModalField>

          <ModalField label="Mood Type">
            <div className="grid grid-cols-3 gap-2">
              {(["Positive", "Neutral", "Negative"] as MoodType[]).map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setType(item)}
                  className="h-11 rounded-lg border text-sm font-medium transition-colors focus:outline-none"
                  style={{
                    borderColor: type === item ? "var(--primary)" : "var(--border)",
                    backgroundColor: type === item ? "rgba(209,61,61,0.06)" : "transparent",
                    color: type === item ? "var(--primary)" : "var(--foreground)",
                  }}
                >
                  {item}
                </button>
              ))}
            </div>
          </ModalField>

          <ModalField label="Score">
            <Input type="number" placeholder="Enter score" value={score} onChange={(event) => setScore(event.target.value)} className="h-11" min={0} max={10} />
          </ModalField>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Create Mood" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}