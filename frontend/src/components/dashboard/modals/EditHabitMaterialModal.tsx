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
    habitTitle?: string;
  } | null;
  onSubmit?: (
    data: {
      id: number;
      title: string;
      material_type: string;
      file?: File;
    },
    onProgress?: (percent: number) => void
  ) => void | Promise<void>;
};

export function EditHabitMaterialModal({ open, onOpenChange, habits, material, onSubmit }: EditHabitMaterialModalProps) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState("PDF");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);

  useEffect(() => {
    if (material) {
      setTitle(material.title);
      const mType = (material.material_type || "PDF").toUpperCase();
      setType(mType === "VIDEO" || mType === "PDF" ? mType : "PDF");
      setFile(null);
      setError(null);
      setSaving(false);
      setUploadProgress(null);
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

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.(
        {
          id: material.id,
          title: nextTitle,
          material_type: type.toLowerCase(),
          file: file ?? undefined,
        },
        (percent) => {
          setUploadProgress(percent);
        }
      );
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update habit material.");
    } finally {
      setSaving(false);
      setUploadProgress(null);
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
            <div className="flex h-11 items-center rounded-md border border-border bg-muted/30 px-3 text-sm text-foreground">
              {material?.habitTitle || "Unknown habit"}
            </div>
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
          {uploadProgress !== null && (
            <div className="mb-4 space-y-1.5">
              <div className="flex justify-between text-xs font-medium text-muted-foreground">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                <div 
                  className="h-full bg-primary transition-all duration-300 ease-out" 
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}
          <ModalFooter onCancel={() => { setFile(null); setError(null); onOpenChange(false); }} confirmLabel="Save Changes" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
