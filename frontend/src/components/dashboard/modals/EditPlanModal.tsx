"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { ModalError, ModalField, ModalFooter } from "./shared";

export type EditPlanData = {
  id: number;
  name: string;
  price: string;
  duration: "monthly" | "yearly" | "lifetime";
  is_active: boolean;
  is_popular: boolean;
};

type EditPlanModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  plan: EditPlanData | null;
  onSubmit?: (data: EditPlanData) => void | Promise<void>;
};

export function EditPlanModal({
  open,
  onOpenChange,
  plan,
  onSubmit,
}: EditPlanModalProps) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [duration, setDuration] = useState<"monthly" | "yearly" | "lifetime">("monthly");
  const [isActive, setIsActive] = useState(true);
  const [isPopular, setIsPopular] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (plan && open) {
      setName(plan.name);
      setPrice(plan.price);
      setDuration(plan.duration);
      setIsActive(plan.is_active);
      setIsPopular(plan.is_popular);
      setError(null);
    }
  }, [plan, open]);

  const handleConfirm = async () => {
    if (!name.trim()) {
      setError("Plan name is required.");
      return;
    }
    if (!plan) {
      setError("No plan selected.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({
        id: plan.id,
        name: name.trim(),
        price: price.trim(),
        duration,
        is_active: isActive,
        is_popular: isPopular,
      });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save plan.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { onOpenChange(value); }}>
      <DialogContent className="sm:max-w-lg rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Plan</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Update plan details.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <ModalField label="Name">
              <Input placeholder="Plan name" value={name} onChange={(event) => setName(event.target.value)} className="h-11" />
            </ModalField>
            <ModalField label="Price">
              <Input placeholder="0.00" value={price} onChange={(event) => setPrice(event.target.value)} className="h-11" />
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
          <ModalFooter onCancel={() => onOpenChange(false)} confirmLabel="Save Plan" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}