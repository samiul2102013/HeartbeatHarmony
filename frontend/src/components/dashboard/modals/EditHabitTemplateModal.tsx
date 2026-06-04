"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ModalError, ModalField, ModalFooter } from "./shared";

type TopicOption = {
  id: number;
  name: string;
};

type EditHabitTemplateModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  categories: TopicOption[];
  initial: {
    id: number;
    category: number;
    activity_name: string;
    description: string;
    duration: number;
    is_active: boolean;
  } | null;
  onSubmit?: (data: {
    id: number;
    category: number;
    activity_name: string;
    description: string;
    duration: number;
    is_active: boolean;
  }) => void | Promise<void>;
};

export function EditHabitTemplateModal({ open, onOpenChange, categories, initial, onSubmit }: EditHabitTemplateModalProps) {
  const [category, setCategory] = useState<string>("");
  const [activityName, setActivityName] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("");
  const [status, setStatus] = useState<"Active" | "Inactive">("Active");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const selectedCategory = categories.find((c) => String(c.id) === category);

  useEffect(() => {
    if (initial) {
      setCategory(String(initial.category));
      setActivityName(initial.activity_name);
      setDescription(initial.description);
      setDuration(String(initial.duration));
      setStatus(initial.is_active ? "Active" : "Inactive");
      setError(null);
    }
  }, [initial]);

  const handleConfirm = async () => {
    if (!initial) return;
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
        id: initial.id,
        category: Number(category),
        activity_name: nextName,
        description: description.trim(),
        duration: dur,
        is_active: status === "Active",
      });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update habit template.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Prebuilt Habit</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Update habit template details.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Category">
            <Select value={category} onValueChange={(v) => setCategory(v ?? "")}>
              <SelectTrigger className="h-11 w-full text-sm">
                <SelectValue placeholder="Select category">{selectedCategory ? <span>{selectedCategory.name}</span> : undefined}</SelectValue>
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

          <ModalField label="Status">
            <Select value={status} onValueChange={(value) => setStatus((value ?? "Active") as "Active" | "Inactive")}>
              <SelectTrigger className="h-11">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Active">Active</SelectItem>
                <SelectItem value="Inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </ModalField>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => onOpenChange(false)} confirmLabel="Save Changes" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
