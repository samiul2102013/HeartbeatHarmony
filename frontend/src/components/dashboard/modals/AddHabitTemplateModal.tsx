"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ModalError, ModalField, ModalFooter } from "./shared";

type TopicOption = {
  id: number;
  name: string;
};

type AddHabitTemplateModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  categories: TopicOption[];
  onSubmit?: (data: {
    category: number;
    activity_name: string;
    description: string;
    duration: number;
    is_active: boolean;
  }) => void | Promise<void>;
};

export function AddHabitTemplateModal({ open, onOpenChange, categories, onSubmit }: AddHabitTemplateModalProps) {
  const [category, setCategory] = useState<string>("");
  const [activityName, setActivityName] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setCategory(categories[0]?.id ? String(categories[0].id) : "");
    setActivityName("");
    setDescription("");
    setDuration("");
    setError(null);
    setSaving(false);
  };

  const handleConfirm = async () => {
    const nextName = activityName.trim();
    if (!nextName) {
      setError("Activity name is required.");
      return;
    }
    if (!category) {
      setError("Please select a category.");
      return;
    }
    const dur = parseInt(duration, 10);
    if (!duration || isNaN(dur) || dur <= 0) {
      setError("Duration must be a positive number (minutes).");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({
        category: Number(category),
        activity_name: nextName,
        description: description.trim(),
        duration: dur,
        is_active: true,
      });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create habit template.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Add Prebuilt Habit</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Create a default habit under a category that users can adopt.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Category">
            <Select value={category} onValueChange={(v) => setCategory(v ?? "")}>
              <SelectTrigger className="h-11 text-sm">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </ModalField>

          <ModalField label="Activity Name">
            <Input placeholder="e.g. Morning Run" value={activityName} onChange={(event) => setActivityName(event.target.value)} className="h-11" />
          </ModalField>

          <ModalField label="Description">
            <Input placeholder="Optional description" value={description} onChange={(event) => setDescription(event.target.value)} className="h-11" />
          </ModalField>

          <ModalField label="Duration (minutes)">
            <Input type="number" placeholder="e.g. 30" value={duration} onChange={(event) => setDuration(event.target.value)} className="h-11" />
          </ModalField>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Add Habit" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
