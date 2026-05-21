"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { ModalError, ModalField, ModalFooter } from "./shared";

export type CreatePlanData = {
  name: string;
  slug: string;
  price: string;
  duration: "monthly" | "yearly" | "lifetime";
  is_active: boolean;
  is_popular: boolean;
};

type AddPlanModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  onSubmit?: (data: CreatePlanData) => void | Promise<void>;
};

export function AddPlanModal({
  open,
  onOpenChange,
  onSubmit,
}: AddPlanModalProps) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [duration, setDuration] = useState<"monthly" | "yearly" | "lifetime">("monthly");
  const [isActive, setIsActive] = useState(true);
  const [isPopular, setIsPopular] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Reset form when modal opens
  const handleOpenChange = (value: boolean) => {
    if (value) {
      setName("");
      setPrice("");
      setDuration("monthly");
      setIsActive(true);
      setIsPopular(false);
      setError(null);
    }
    onOpenChange(value);
  };

  const handleConfirm = async () => {
    if (!name.trim()) {
      setError("Plan name is required.");
      return;
    }
    if (!price.trim()) {
      setError("Price is required.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const slug = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
      await onSubmit?.({
        name: name.trim(),
        slug,
        price: price.trim(),
        duration,
        is_active: isActive,
        is_popular: isPopular,
      });
      handleOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create plan.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Create Plan</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Add a new pricing plan.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <ModalField label="Name">
              <Input placeholder="Plan name" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
            </ModalField>
            <ModalField label="Price">
              <Input placeholder="0.00" value={price} onChange={(event) => setPrice(event.target.value)} className="h-11" type="number" step="0.01" />
            </ModalField>
          </div>

          <ModalField label="Duration">
            <select
              value={duration}
              onChange={(e) => setDuration(e.target.value as any)}
              className="h-11 w-full rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
              <option value="lifetime">Lifetime</option>
            </select>
          </ModalField>

          <div className="flex items-center gap-4">
            <label className="inline-flex items-center gap-2 text-sm text-foreground">
              <Checkbox checked={isActive} onCheckedChange={(checked) => setIsActive(Boolean(checked))} />
              Active
            </label>
            <label className="inline-flex items-center gap-2 text-sm text-foreground">
              <Checkbox checked={isPopular} onCheckedChange={(checked) => setIsPopular(Boolean(checked))} />
              Popular
            </label>
          </div>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => handleOpenChange(false)} confirmLabel="Create Plan" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
