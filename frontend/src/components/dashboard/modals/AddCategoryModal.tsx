"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ModalError, ModalField, ModalFooter } from "./shared";

type AddCategoryModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  onSubmit?: (data: { name: string }) => void | Promise<void>;
};

export function AddCategoryModal({ open, onOpenChange, onSubmit }: AddCategoryModalProps) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setName("");
    setError(null);
    setSaving(false);
  };

  const handleConfirm = async () => {
    const nextName = name.trim();
    if (!nextName) {
      setError("Category name is required.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({ name: nextName });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create category.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Add New Category</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Create a category that can be reused across the dashboard.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Name">
            <Input placeholder="Enter name" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
          </ModalField>
          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Create Category" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}