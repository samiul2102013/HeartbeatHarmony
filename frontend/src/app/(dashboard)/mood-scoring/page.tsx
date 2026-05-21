"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { AdminMood, listMoods, updateMood } from "@/lib/index";
import { ChevronDown, Pencil, Search } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type MoodType = "Positive" | "Neutral" | "Negative";

type MoodRow = {
  id: number;
  name: string;
  type: MoodType;
  score: number;
};

function scoreToType(score: number): MoodType {
  return score >= 7 ? "Positive" : score >= 4 ? "Neutral" : "Negative";
}

function mapMood(mood: AdminMood): MoodRow {
  return { id: mood.id, name: mood.name ?? "", type: scoreToType(mood.score ?? 5), score: mood.score ?? 5 };
}

function unwrapList<T>(res: unknown): T[] {
  if (!res) return [];
  if (Array.isArray(res)) return res as T[];
  const o = res as Record<string, unknown>;
  if (Array.isArray(o.results)) return o.results as T[];
  if (Array.isArray(o.data)) return o.data as T[];
  return [];
}

// ── Inline Edit Modal ────────────────────────────────────────────────────────
function EditMoodScoreModal({
  mood, open, onOpenChange, onSave,
}: {
  mood: MoodRow | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (id: number, score: number, type: MoodType) => Promise<void>;
}) {
  const [score, setScore] = useState("");
  const [type, setType] = useState<MoodType>("Positive");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!mood) return;
    setScore(String(mood.score)); setType(mood.type); setError(null);
  }, [mood]);

  const handleSave = async () => {
    const scoreNum = Number(score);
    if (Number.isNaN(scoreNum) || scoreNum < 1 || scoreNum > 10) {
      setError("Score must be between 1 and 10."); return;
    }
    setSaving(true); setError(null);
    try {
      await onSave(mood!.id, scoreNum, type);
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save.");
    } finally { setSaving(false); }
  };

  if (!mood) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Edit Mood — {mood.name}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
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
          <div className="space-y-1.5">
            <Label className="text-sm font-semibold">Score (1–10)</Label>
            <Input type="number" value={score} onChange={(e) => setScore(e.target.value)} className="h-11" min={1} max={10} />
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

// ── Page ─────────────────────────────────────────────────────────────────────
export default function MoodScoringPage() {
  const [search, setSearch] = useState("");
  const [moods, setMoods] = useState<MoodRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editTarget, setEditTarget] = useState<MoodRow | null>(null);

  const loadMoods = useCallback(async () => {
    try {
      setLoading(true); setError(null);
      const res = await listMoods();
      setMoods(unwrapList<AdminMood>(res).map(mapMood));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load moods");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void loadMoods(); }, [loadMoods]);

  const filtered = useMemo(
    () => moods.filter((m) => (m.name ?? "").toLowerCase().includes(search.toLowerCase())),
    [moods, search]
  );

  const handleSave = async (id: number, score: number, type: MoodType) => {
    // Derive a matching emoji from type so the API stays consistent
    const emoji = type === "Positive" ? "😊" : type === "Neutral" ? "😐" : "😟";
    await updateMood(id, { score, emoji });
    await loadMoods();
  };

  const TYPE_COLORS: Record<MoodType, string> = {
    Positive: "#16a34a",
    Neutral: "var(--muted-foreground)",
    Negative: "#ef4444",
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Mood Scoring Management</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Configure moods, scoring weights, and emotional visibility.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="relative w-64">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="h-9 pl-9 text-sm" />
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
              {["Mood Name", "Type", "Score", "Action"].map((h) => (
                <TableHead key={h} className={`${h === "Mood Name" ? "pl-5 " : ""}text-xs font-semibold uppercase tracking-wide text-muted-foreground`}>{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={4} className="py-12 text-center text-sm text-muted-foreground">Loading moods...</TableCell></TableRow>
            ) : filtered.length === 0 ? (
              <TableRow><TableCell colSpan={4} className="py-12 text-center text-sm text-muted-foreground">No moods found.</TableCell></TableRow>
            ) : (
              filtered.map((mood) => (
                <TableRow key={mood.id} className="border-border transition-colors hover:bg-muted/40">
                  <TableCell className="py-3.5 pl-5 text-sm font-medium text-foreground">{mood.name}</TableCell>
                  <TableCell className="py-3.5">
                    <span className="text-sm font-medium" style={{ color: TYPE_COLORS[mood.type] }}>{mood.type}</span>
                  </TableCell>
                  <TableCell className="py-3.5 text-sm text-foreground">{mood.score}</TableCell>
                  <TableCell className="py-3.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                        Action <ChevronDown className="h-3 w-3" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-44 rounded-lg">
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm" onClick={() => setEditTarget(mood)}>
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit Score & Type
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <EditMoodScoreModal
        mood={editTarget}
        open={!!editTarget}
        onOpenChange={(v) => { if (!v) setEditTarget(null); }}
        onSave={handleSave}
      />
    </div>
  );
}