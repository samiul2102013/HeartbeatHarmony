"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useEffect, useState } from "react";
import type { MoodRow } from "./page";

const PRESET_COLORS = [
  "#22c55e", "#f59e0b", "#818cf8", "#6b7280", "#64748b",
  "#ef4444", "#3b82f6", "#a78bfa", "#f472b6", "#ec4899",
  "#b91c1c", "#fca5a5", "#111827", "#fb923c", "#86efac",
];

type MoodType = "Positive" | "Neutral" | "Negative";

interface EditMoodDialogProps {
  mood: MoodRow | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (updated: MoodRow) => Promise<void>;
}

export function EditMoodDialog({ mood, open, onOpenChange, onSave }: EditMoodDialogProps) {
  const [name, setName] = useState("");
  const [emoji, setEmoji] = useState("");
  const [emojiFile, setEmojiFile] = useState<File | null>(null);
  const [emojiFileName, setEmojiFileName] = useState("");
  const [color, setColor] = useState(PRESET_COLORS[0]);
  const [type, setType] = useState<MoodType>("Positive");
  const [score, setScore] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!mood) return;
    setName(mood.name); setEmoji(mood.emoji); setEmojiFile(mood.emojiFile ?? null);
    setEmojiFileName(mood.svg ? "Current image" : "");
    setColor(mood.color || PRESET_COLORS[0]);
    setType(mood.type ?? "Positive");
    setScore(String(mood.score ?? ""));
    setError(null);
  }, [mood]);

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

  const handleSave = async () => {
    if (!mood) return;
    const nextName = name.trim();
    if (!nextName) { setError("Name is required."); return; }
    const scoreNum = Number(score);
    if (score.trim() && (Number.isNaN(scoreNum) || scoreNum < 1 || scoreNum > 10)) {
      setError("Score must be between 1 and 10."); return;
    }
    setSaving(true); setError(null);
    try {
      await onSave({ ...mood, name: nextName, emoji: emoji.trim(), emojiFile: emojiFile, color, type, score: scoreNum || mood.score });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save changes.");
    } finally { setSaving(false); }
  };

  if (!mood) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Mood Category</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-sm font-semibold">Name</Label>
              <Input placeholder="Enter name" value={name} onChange={(e) => setName(e.target.value)} className="h-11" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-sm font-semibold">Image</Label>
              <label className="flex h-11 cursor-pointer items-center justify-between gap-3 rounded-md border border-dashed border-border px-3 text-sm text-muted-foreground transition-colors hover:bg-muted/40">
                <span className="truncate">{emojiFileName || "Choose image file"}</span>
                <span className="shrink-0 rounded bg-muted px-2 py-1 text-xs font-medium text-foreground">Browse</span>
                <input type="file" accept="image/*" className="hidden" onChange={handleSvgFileChange} />
              </label>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-sm font-semibold">Mood Type</Label>
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
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-sm font-semibold">Score (1–10)</Label>
              <Input type="number" placeholder="e.g. 7" value={score} onChange={(e) => setScore(e.target.value)} className="h-11" min={1} max={10} />
            </div>
            <div className="space-y-1.5">
              <Label className="text-sm font-semibold">Color</Label>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {PRESET_COLORS.map((c) => (
                  <button key={c} type="button" onClick={() => setColor(c)}
                    className="h-6 w-6 rounded-md transition-transform hover:scale-110 focus:outline-none"
                    style={{ backgroundColor: c, boxShadow: color === c ? `0 0 0 2px white, 0 0 0 3px ${c}` : undefined }} />
                ))}
              </div>
            </div>
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <DialogFooter className="gap-2 pt-6">
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)} disabled={saving}>Cancel</Button>
          <Button size="sm" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={handleSave} disabled={saving}>
            {saving ? "Saving…" : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}