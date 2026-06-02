"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ModalError, ModalField, ModalFooter } from "./shared";

type HabitOption = {
  id: number;
  activity_name: string;
  user_username?: string;
};

type AddHabitMaterialModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  habits: HabitOption[];
  onSubmit?: (data: {
    habit: number;
    title: string;
    material_type: string;
    file?: File;
  }) => void | Promise<void>;
};

export function AddHabitMaterialModal({ open, onOpenChange, habits, onSubmit }: AddHabitMaterialModalProps) {
  const [habitId, setHabitId] = useState<string>("");
  const [title, setTitle] = useState("");
  const [type, setType] = useState("PDF");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const selectedHabit = habits.find((h) => String(h.id) === habitId);

  const reset = () => {
    setHabitId(habits[0]?.id ? String(habits[0].id) : "");
    setTitle("");
    setType("PDF");
    setFile(null);
    setError(null);
    setSaving(false);
  };

  useEffect(() => {
    if (habits.length > 0 && !habitId) {
      setHabitId(String(habits[0].id));
    }
  }, [habits, habitId]);

  const handleConfirm = async () => {
    const nextTitle = title.trim();
    if (!nextTitle) {
      setError("Material title is required.");
      return;
    }
    if (!habitId) {
      setError("Please select a habit.");
      return;
    }
    if (!file) {
      setError(`Please upload a ${type} file.`);
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({
        habit: Number(habitId),
        title: nextTitle,
        material_type: type.toLowerCase(),
        file: file ?? undefined,
      });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create habit material.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Add Material Under Habit</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Attach study resources to a habit.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Habit">
            <Select value={habitId} onValueChange={(v) => setHabitId(v ?? "")}>
              <SelectTrigger className="h-auto min-h-11 text-sm py-2 [&_[data-slot=select-value]]:line-clamp-none [&_[data-slot=select-value]]:whitespace-normal [&_[data-slot=select-value]]:break-words">
                <SelectValue placeholder="Select habit">
                  {selectedHabit ? (
                    <span className="block whitespace-normal break-words">
                      {selectedHabit.activity_name}
                      {selectedHabit.user_username ? ` • ${selectedHabit.user_username}` : ""}
                    </span>
                  ) : undefined}
                </SelectValue>
              </SelectTrigger>
              <SelectContent alignItemWithTrigger={false} className="min-w-[28rem] max-w-[40rem]">
                {habits.map((habit) => (
                  <SelectItem
                    key={habit.id}
                    value={String(habit.id)}
                    className="[&_span]:whitespace-normal [&_span]:break-words py-2"
                  >
                    <span className="block whitespace-normal break-words">
                      <span className="font-medium">{habit.activity_name}</span>
                      {habit.user_username ? (
                        <span className="text-muted-foreground"> • {habit.user_username}</span>
                      ) : ""}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </ModalField>

          <ModalField label="Title">
            <Input placeholder="Enter title" value={title} onChange={(event) => setTitle(event.target.value)} className="h-11" />
          </ModalField>

          <ModalField label="Material Type">
            <Select value={type} onValueChange={(v) => { setType(v ?? "PDF"); setFile(null); }}>
              <SelectTrigger className="h-11 text-sm">
                <SelectValue placeholder="Choose type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PDF">PDF</SelectItem>
                <SelectItem value="Video">Video</SelectItem>
              </SelectContent>
            </Select>
          </ModalField>

          <ModalField label={type === "PDF" ? "PDF File" : "Video File"}>
            <Input
              type="file"
              accept={type === "PDF" ? ".pdf,application/pdf" : "video/*"}
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="h-11"
            />
            {file && <p className="mt-1 text-xs text-muted-foreground">Selected: {file.name}</p>}
          </ModalField>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Add Material" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
