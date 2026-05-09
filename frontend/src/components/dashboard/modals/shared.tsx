"use client";

import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

export function ModalField({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label className="text-sm font-semibold text-foreground">{label}</Label>
      {children}
    </div>
  );
}

export function ModalError({ message }: { message: string | null }) {
  if (!message) return null;

  return (
    <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800" role="alert">
      {message}
    </p>
  );
}

export function ModalFooter({
  onCancel,
  confirmLabel,
  onConfirm,
  loading = false,
  loadingLabel,
}: {
  onCancel: () => void;
  confirmLabel: string;
  onConfirm?: () => void;
  loading?: boolean;
  loadingLabel?: string;
}) {
  return (
    <div className="flex gap-3 pt-2">
      <Button type="button" variant="outline" className="flex-1 h-11 text-sm font-medium" onClick={onCancel} disabled={loading}>
        Cancel
      </Button>
      <Button
        type="button"
        className="flex-1 h-11 text-sm font-medium"
        style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
        onClick={onConfirm}
        disabled={loading}
      >
        {loading ? (loadingLabel ?? `${confirmLabel}...`) : confirmLabel}
      </Button>
    </div>
  );
}