"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ModalError, ModalField, ModalFooter } from "./shared";

export type CategoryDialogValue = {
  name: string;
  status: "Active" | "Inactive";
};

type EditCategoryModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  initial: CategoryDialogValue | null;
  onSubmit?: (data: { name: string; is_active: boolean }) => void | Promise<void>;
};

export function EditCategoryModal({ open, onOpenChange, initial, onSubmit }: EditCategoryModalProps) {
  const [name, setName] = useState("");
  const [status, setStatus] = useState<"Active" | "Inactive">("Active");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open || !initial) return;
    setName(initial.name ?? "");
    setStatus(initial.status);
    setError(null);
  }, [initial, open]);

  const reset = () => {
    setName("");
    setStatus("Active");
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
      await onSubmit?.({ name: nextName, is_active: status === "Active" });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update category.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Category</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Name">
            <Input placeholder="Enter category name" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
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
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Save Changes" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}