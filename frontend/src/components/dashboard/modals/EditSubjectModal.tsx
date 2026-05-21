"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ModalError, ModalField, ModalFooter } from "./shared";

type EditSubjectModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  subject: {
    id: number;
    name: string;
  } | null;
  onSubmit?: (data: { id: number; name: string }) => void | Promise<void>;
};

export function EditSubjectModal({ open, onOpenChange, subject, onSubmit }: EditSubjectModalProps) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (subject) {
      setName(subject.name);
      setError(null);
      setSaving(false);
    }
  }, [subject, open]);

  const handleConfirm = async () => {
    const nextName = name.trim();
    if (!nextName) {
      setError("Subject name is required.");
      return;
    }

    if (!subject) {
      setError("No subject selected.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({ id: subject.id, name: nextName });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update subject.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) setError(null); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Subject</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Update the subject name.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Subject Name">
            <Input placeholder="Enter subject name" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
          </ModalField>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { setError(null); onOpenChange(false); }} confirmLabel="Save Changes" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
