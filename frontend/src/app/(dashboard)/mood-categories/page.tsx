"use client";

import { AddMoodCategoryModal } from "@/components/dashboard/modals/AddMoodCategoryModal";
import { EditMoodDialog } from "./edit-mood-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { AdminMood, createMood, deleteMood, listMoods, updateMood } from "@/lib/index";
import { ChevronDown, Pencil, Plus, Search, ToggleLeft, Trash2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

export type MoodRow = {
  id: number;
  name: string;
  emoji: string;
  svg: string | null;
  emojiFile?: File | null;
  color: string;
  type: "Positive" | "Neutral" | "Negative";
  score: number;
  status: "Active" | "Inactive";
};

const MOOD_COLORS = ["#22c55e","#818cf8","#f59e0b","#6b7280","#ef4444","#3b82f6","#a78bfa","#c084fc"];

function hashColor(name: string) {
  return MOOD_COLORS[name.split("").reduce((s, c) => s + c.charCodeAt(0), 0) % MOOD_COLORS.length];
}

// Derive type from score so the table stays consistent
function scoreToType(score: number): MoodRow["type"] {
  return score >= 7 ? "Positive" : score >= 4 ? "Neutral" : "Negative";
}

function mapMood(mood: AdminMood): MoodRow {
  return {
    id: mood.id,
    name: mood.name ?? "",
    emoji: mood.emoji ?? "",
    svg: mood.svg ?? null,
    color: hashColor(mood.name ?? ""),
    type: scoreToType(mood.score ?? 5),
    score: mood.score ?? 5,
    status: mood.is_active ? "Active" : "Inactive",
  };
}

function MoodSvgPreview({ svg, label }: { svg: string | null; label: string }) {
  if (!svg) {
    return <span className="text-sm text-foreground">-</span>;
  }

  const trimmed = svg.trim();
  const isSvgMarkup = trimmed.startsWith("<svg");
  const isUrl = trimmed.startsWith("http") || trimmed.startsWith("/");

  if (isUrl) {
    return (
      <img
        src={trimmed}
        alt={label}
        className="inline-flex h-7 w-7 items-center justify-center overflow-hidden rounded-md border border-border bg-background object-contain p-0.5"
      />
    );
  }

  if (isSvgMarkup) {
    return (
      <span
        className="inline-flex h-7 w-7 items-center justify-center overflow-hidden rounded-md border border-border bg-background"
        aria-label={label}
        dangerouslySetInnerHTML={{ __html: trimmed }}
      />
    );
  }

  return <span className="text-sm text-foreground">{trimmed || "-"}</span>;
}

function unwrapList<T>(res: unknown): T[] {
  if (!res) return [];
  if (Array.isArray(res)) return res as T[];
  const o = res as Record<string, unknown>;
  if (Array.isArray(o.results)) return o.results as T[];
  if (Array.isArray(o.data)) return o.data as T[];
  if (typeof (o as any).id === "number") return [o as T];
  return [];
}

export default function MoodCategoriesPage() {
  const [search, setSearch] = useState("");
  const [moods, setMoods] = useState<MoodRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<MoodRow | null>(null);

  const loadMoods = useCallback(async () => {
    try {
      setLoading(true); setError(null);
      const res = await listMoods();
      setMoods(unwrapList<AdminMood>(res).map(mapMood));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load mood categories");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void loadMoods(); }, [loadMoods]);

  const filtered = useMemo(
    () => moods.filter((m) => (m.name ?? "").toLowerCase().includes(search.toLowerCase())),
    [moods, search]
  );

  const handleAdd = async (data: { name: string; emoji: string; emojiFile?: File | null; color: string; type: MoodRow["type"]; score: number }) => {
    const formData = new FormData();
    formData.append("name", data.name);
    if (data.emojiFile) {
      formData.append("svg", data.emojiFile);
    }
    if (data.emoji) {
      formData.append("emoji", data.emoji);
    }
    formData.append("score", String(data.score));
    formData.append("is_active", "true");
    await createMood(formData);
    await loadMoods();
  };

  const handleEdit = async (updated: MoodRow) => {
    const formData = new FormData();
    formData.append("name", updated.name);
    if (updated.emojiFile) {
      formData.append("svg", updated.emojiFile);
    }
    if (updated.emoji) {
      formData.append("emoji", updated.emoji);
    }
    formData.append("score", String(updated.score));
    formData.append("is_active", updated.status === "Active" ? "true" : "false");
    await updateMood(updated.id, formData);
    await loadMoods();
  };

  const toggleStatus = async (id: number) => {
    const current = moods.find((m) => m.id === id);
    if (!current) return;
    try {
      setError(null);
      await updateMood(id, { is_active: current.status !== "Active" });
      await loadMoods();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update status");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setError(null);
      await deleteMood(id);
      await loadMoods();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete mood category");
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Mood Categories</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Manage mood categories with emoji, colors, and scoring.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="h-9 pl-9 text-sm" />
        </div>
        <Button className="h-9 gap-1.5 text-sm font-medium" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" /> Add New Mood Category
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
              {["Name", "Image", "Color", "Type", "Score", "Status", "Action"].map((h) => (
                <TableHead key={h} className={`${h === "Name" ? "pl-5 " : ""}text-xs font-semibold uppercase tracking-wide text-muted-foreground`}>{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={7} className="py-12 text-center text-sm text-muted-foreground">Loading mood categories...</TableCell></TableRow>
            ) : filtered.length === 0 ? (
              <TableRow><TableCell colSpan={7} className="py-12 text-center text-sm text-muted-foreground">No mood categories found.</TableCell></TableRow>
            ) : (
              filtered.map((mood) => (
                <TableRow key={mood.id} className="border-border transition-colors hover:bg-muted/40">
                  <TableCell className="py-3.5 pl-5 text-sm font-medium text-foreground">{mood.name}</TableCell>
                  <TableCell className="py-3.5">
                    <MoodSvgPreview svg={mood.svg || mood.emoji} label={mood.name} />
                  </TableCell>
                  <TableCell className="py-3.5">
                    <div className="h-6 w-6 rounded-md ring-1 ring-black/10" style={{ backgroundColor: mood.color }} />
                  </TableCell>
                  <TableCell className="py-3.5">
                    <span className="text-sm font-medium" style={{ color: mood.type === "Positive" ? "#16a34a" : mood.type === "Negative" ? "#ef4444" : "var(--muted-foreground)" }}>
                      {mood.type}
                    </span>
                  </TableCell>
                  <TableCell className="py-3.5 text-sm text-foreground">{mood.score}</TableCell>
                  <TableCell className="py-3.5">
                    <span className="text-sm font-medium" style={{ color: mood.status === "Active" ? "#16a34a" : "var(--muted-foreground)" }}>{mood.status}</span>
                  </TableCell>
                  <TableCell className="py-3.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                        Action <ChevronDown className="h-3 w-3" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-44 rounded-lg">
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm" onClick={() => setEditTarget(mood)}>
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm" onClick={() => void toggleStatus(mood.id)}>
                          <ToggleLeft className="h-3.5 w-3.5 text-muted-foreground" />
                          {mood.status === "Active" ? "Deactivate" : "Activate"}
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive" onClick={() => void handleDelete(mood.id)}>
                          <Trash2 className="h-3.5 w-3.5" /> Delete
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

      <AddMoodCategoryModal open={addOpen} onOpenChange={setAddOpen} onSubmit={handleAdd} />
      <EditMoodDialog mood={editTarget} open={!!editTarget} onOpenChange={(v) => { if (!v) setEditTarget(null); }} onSave={handleEdit} />
    </div>
  );
}