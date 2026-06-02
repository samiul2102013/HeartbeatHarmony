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

type EditHabitMaterialModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  habits: HabitOption[];
  material: {
    id: number;
    title: string;
    material_type: string;
    habitId: number;
  } | null;
  onSubmit?: (data: {
    id: number;
    habit: number;
    title: string;
    material_type: string;
    file?: File;
  }) => void | Promise<void>;
};

export function EditHabitMaterialModal({ open, onOpenChange, habits, material, onSubmit }: EditHabitMaterialModalProps) {
  const [habitId, setHabitId] = useState<string>("");
  const [title, setTitle] = useState("");
  const [type, setType] = useState("PDF");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const selectedHabit = habits.find((h) => String(h.id) === habitId);

  useEffect(() => {
    if (material) {
      setHabitId(String(material.habitId));
      setTitle(material.title);
      const mType = (material.material_type || "PDF").toUpperCase();
      setType(mType === "VIDEO" || mType === "PDF" ? mType : "PDF");
      setFile(null);
      setError(null);
      setSaving(false);
    }
  }, [material, open]);

  const handleConfirm = async () => {
    if (!material) {
      setError("No material selected.");
      return;
    }
    const nextTitle = title.trim();
    if (!nextTitle) {
      setError("Material title is required.");
      return;
    }
    if (!habitId) {
      setError("Please select a habit.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({
        id: material.id,
        habit: Number(habitId),
        title: nextTitle,
        material_type: type.toLowerCase(),
        file: file ?? undefined,
      });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update habit material.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) { setFile(null); setError(null); } onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Material Under Habit</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Update habit material details.</DialogDescription>
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

          <ModalField label={type === "PDF" ? "Replace PDF File (optional)" : "Replace Video File (optional)"}>
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
          <ModalFooter onCancel={() => { setFile(null); setError(null); onOpenChange(false); }} confirmLabel="Save Changes" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
