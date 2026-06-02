"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ModalError, ModalField, ModalFooter } from "./shared";

const PRESET_COLORS = [
  "#22c55e", "#f59e0b", "#818cf8", "#6b7280", "#64748b",
  "#ef4444", "#3b82f6", "#a78bfa", "#f472b6", "#ec4899",
  "#b91c1c", "#fca5a5", "#111827", "#fb923c", "#86efac",
];

type MoodType = "Positive" | "Neutral" | "Negative";

type AddMoodCategoryModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  onSubmit?: (data: { name: string; emoji: string; emojiFile?: File | null; color: string; type: MoodType; score: number }) => void | Promise<void>;
};

export function AddMoodCategoryModal({ open, onOpenChange, onSubmit }: AddMoodCategoryModalProps) {
  const [name, setName] = useState("");
  const [emoji, setEmoji] = useState("");
  const [emojiFile, setEmojiFile] = useState<File | null>(null);
  const [emojiFileName, setEmojiFileName] = useState("");
  const [color, setColor] = useState(PRESET_COLORS[0]);
  const [type, setType] = useState<MoodType>("Positive");
  const [score, setScore] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setName(""); setEmoji(""); setEmojiFile(null); setEmojiFileName(""); setColor(PRESET_COLORS[0]);
    setType("Positive"); setScore(""); setError(null); setSaving(false);
  };

  const handleSvgFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Accept any image format. Reject only non-image files.
    if (!file.type.startsWith("image/")) {
      setError("Please choose an image file (PNG, JPG, SVG, WebP, GIF).");
      event.target.value = "";
      return;
    }

    try {
      // For SVG, keep the old behavior of storing the markup text in `emoji`
      // so old backends/clients still work. For raster images, leave `emoji`
      // empty — the file is uploaded as `svg` and the backend stores it.
      if (file.type === "image/svg+xml") {
        const content = await file.text();
        setEmoji(content);
      } else {
        setEmoji("");
      }
      setEmojiFile(file);
      setEmojiFileName(file.name);
      setError(null);
    } catch {
      setError("Unable to read the image file.");
      event.target.value = "";
    }
  };

  const handleConfirm = async () => {
    const nextName = name.trim();
    if (!nextName) { setError("Name is required."); return; }
    const scoreNum = Number(score);
    if (score.trim() && (Number.isNaN(scoreNum) || scoreNum < 1 || scoreNum > 10)) {
      setError("Score must be between 1 and 10."); return;
    }
    setSaving(true); setError(null);
    try {
      await onSubmit?.({ name: nextName, emoji: emoji.trim(), emojiFile: emojiFile, color, type, score: scoreNum || 5 });
      reset(); onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create mood category.");
    } finally { setSaving(false); }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) reset(); onOpenChange(v); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Add New Mood Category</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Choose a label, color, type and score for this mood.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Name + SVG */}
          <div className="grid grid-cols-2 gap-3">
            <ModalField label="Name">
              <Input placeholder="Enter name" value={name} onChange={(e) => setName(e.target.value)} className="h-11" />
            </ModalField>
            <ModalField label="Image">
              <label className="flex h-11 cursor-pointer items-center justify-between gap-3 rounded-md border border-dashed border-border px-3 text-sm text-muted-foreground transition-colors hover:bg-muted/40">
                <span className="truncate">{emojiFileName || "Choose image file"}</span>
                <span className="shrink-0 rounded bg-muted px-2 py-1 text-xs font-medium text-foreground">Browse</span>
                <input type="file" accept="image/*" className="hidden" onChange={handleSvgFileChange} />
              </label>
            </ModalField>
          </div>

          {/* Type */}
          <ModalField label="Mood Type">
            <div className="grid grid-cols-3 gap-2">
              {(["Positive", "Neutral", "Negative"] as MoodType[]).map((t) => (
                <button key={t} type="button" onClick={() => setType(t)}
                  className="h-10 rounded-lg border text-sm font-medium transition-colors focus:outline-none"
                  style={{
                    borderColor: type === t ? "var(--primary)" : "var(--border)",
                    backgroundColor: type === t ? "rgba(209,61,61,0.06)" : "transparent",
                    color: type === t ? "var(--primary)" : "var(--foreground)",
                  }}>
                  {t}
                </button>
              ))}
            </div>
          </ModalField>

          {/* Score + Color */}
          <div className="grid grid-cols-2 gap-3">
            <ModalField label="Score (1–10)">
              <Input type="number" placeholder="e.g. 7" value={score} onChange={(e) => setScore(e.target.value)} className="h-11" min={1} max={10} />
            </ModalField>
            <ModalField label="Color">
              <div className="flex flex-wrap gap-1.5 pt-1">
                {PRESET_COLORS.map((c) => (
                  <button key={c} type="button" onClick={() => setColor(c)}
                    className="h-6 w-6 rounded-md transition-transform hover:scale-110 focus:outline-none"
                    style={{ backgroundColor: c, boxShadow: color === c ? `0 0 0 2px white, 0 0 0 3px ${c}` : undefined }} />
                ))}
              </div>
            </ModalField>
          </div>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Create Mood Category" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}