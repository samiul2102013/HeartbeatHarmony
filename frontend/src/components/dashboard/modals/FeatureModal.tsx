"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { ModalError, ModalField, ModalFooter } from "./shared";

export type FeatureFormData = {
  id?: number;
  plan: number;
  title: string;
  is_included: boolean;
  order: number;
};

type FeatureModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  planName: string;
  feature: FeatureFormData | null;
  onSubmit?: (data: FeatureFormData) => void | Promise<void>;
};

export function FeatureModal({ open, onOpenChange, planName, feature, onSubmit }: FeatureModalProps) {
  const [title, setTitle] = useState("");
  const [isIncluded, setIsIncluded] = useState(true);
  const [order, setOrder] = useState("0");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    setTitle(feature?.title ?? "");
    setIsIncluded(feature?.is_included ?? true);
    setOrder(String(feature?.order ?? 0));
    setError(null);
  }, [feature, open]);

  const handleConfirm = async () => {
    const nextTitle = title.trim();
    if (!nextTitle) {
      setError("Feature name is required.");
      return;
    }

    const nextOrder = Number(order);
    if (!Number.isFinite(nextOrder) || nextOrder < 0) {
      setError("Feature order must be a valid number.");
      return;
    }

    if (!feature) {
      setError("No plan selected.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({
        id: feature.id,
        plan: feature.plan,
        title: nextTitle,
        is_included: isIncluded,
        order: nextOrder,
      });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save feature.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">
            {feature?.id ? "Edit Feature" : "Add Feature"}
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            {planName}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Feature Name">
            <Input placeholder="Feature name" value={title} onChange={(event) => setTitle(event.target.value)} className="h-11" />
          </ModalField>

          <div className="grid grid-cols-2 gap-3">
            <ModalField label="Order">
              <Input type="number" min={0} value={order} onChange={(event) => setOrder(event.target.value)} className="h-11" />
            </ModalField>

            <div className="space-y-1.5">
              <label className="inline-flex items-center gap-2 pt-7 text-sm text-foreground">
                <Checkbox checked={isIncluded} onCheckedChange={(checked) => setIsIncluded(Boolean(checked))} />
                Included
              </label>
            </div>
          </div>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter
            onCancel={() => onOpenChange(false)}
            confirmLabel={feature?.id ? "Save Feature" : "Add Feature"}
            onConfirm={handleConfirm}
            loading={saving}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}