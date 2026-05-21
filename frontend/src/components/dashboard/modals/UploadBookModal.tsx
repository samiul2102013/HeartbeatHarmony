"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ModalError, ModalField, ModalFooter } from "./shared";

type UploadBookModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  onSubmit?: (data: { name: string; date: string }) => void | Promise<void>;
};

export function UploadBookModal({ open, onOpenChange, onSubmit }: UploadBookModalProps) {
  const [name, setName] = useState("");
  const [date, setDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setName("");
    setDate("");
    setError(null);
    setSaving(false);
  };

  const handleConfirm = async () => {
    if (!name.trim()) {
      setError("Subject name is required.");
      return;
    }

    if (!date) {
      setError("Please select a date.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({ name: name.trim(), date });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to upload book.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-2xl rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-3xl font-bold text-foreground">Upload Book</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Attach a subject resource and its publication date.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <ModalField label="Subject Name">
              <Input placeholder="Enter title" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
            </ModalField>

            <ModalField label="Date">
              <Input type="date" value={date} onChange={(event) => setDate(event.target.value)} className="h-11" />
            </ModalField>
          </div>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Upload" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}