"use client";

import { AddHabitTemplateModal } from "@/components/dashboard/modals/AddHabitTemplateModal";
import { EditHabitTemplateModal } from "@/components/dashboard/modals/EditHabitTemplateModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ChevronDown, Pencil, Plus, Search, ToggleLeft, Trash2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import {
  listCategories,
  listHabitTemplates,
  createHabitTemplate,
  updateHabitTemplate,
  deleteHabitTemplate,
} from "@/lib/index";
import type { AdminCategory, HabitTemplate } from "@/lib/index";

function normalizeResponse<T>(res: unknown): T[] {
  if (!res) return [];
  if (Array.isArray(res)) return res as T[];
  const obj = res as Record<string, unknown>;
  if (Array.isArray(obj.results)) return obj.results as T[];
  if (Array.isArray(obj.data)) return obj.data as T[];
  return [];
}

type HabitRow = {
  id: number;
  category: string;
  category_name?: string;
  activity_name: string;
  duration: number;
  status: "Active" | "Inactive";
};

function mapTemplate(t: HabitTemplate): HabitRow {
  return {
    id: t.id,
    category: t.category_name || "Uncategorized",
    category_name: t.category_name || undefined,
    activity_name: t.activity_name,
    duration: t.duration,
    status: t.is_active ? "Active" : "Inactive",
  };
}

export default function HabitsPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [habits, setHabits] = useState<HabitRow[]>([]);
  const [categories, setCategories] = useState<AdminCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<HabitTemplate | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [catRes, habitRes] = await Promise.all([
        listCategories(),
        listHabitTemplates(selectedCategory !== "all" ? { category: Number(selectedCategory) } : undefined),
      ]);
      const cats = normalizeResponse<AdminCategory>(catRes);
      setCategories(cats);
      const templates = normalizeResponse<HabitTemplate>(habitRes);
      setHabits(templates.map(mapTemplate));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load habits");
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const filtered = useMemo(
    () =>
      habits.filter((h) =>
        (h.activity_name || "").toLowerCase().includes(search.toLowerCase()) ||
        (h.category || "").toLowerCase().includes(search.toLowerCase())
      ),
    [habits, search]
  );

  const handleAdd = async (data: {
    category: number;
    activity_name: string;
    description: string;
    duration: number;
    is_active: boolean;
  }) => {
    await createHabitTemplate(data);
    await loadData();
  };

  const handleEdit = async (data: {
    id: number;
    category: number;
    activity_name: string;
    description: string;
    duration: number;
    is_active: boolean;
  }) => {
    await updateHabitTemplate(data.id, {
      category: data.category,
      activity_name: data.activity_name,
      description: data.description,
      duration: data.duration,
      is_active: data.is_active,
    });
    setEditTarget(null);
    await loadData();
  };

  const toggleStatus = async (id: number) => {
    const current = habits.find((h) => h.id === id);
    if (!current) return;
    try {
      setError(null);
      await updateHabitTemplate(id, { is_active: current.status !== "Active" });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update status");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setError(null);
      await deleteHabitTemplate(id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete habit template");
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Habits</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Manage prebuilt habits under each category for users to adopt.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search habits"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-9 pl-9 text-sm"
            />
          </div>
          <Select value={selectedCategory} onValueChange={(v) => setSelectedCategory(v ?? "all")}>
            <SelectTrigger className="h-9 w-48 text-sm">
              <SelectValue placeholder="All categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {categories.map((c) => (
                <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button
          className="h-9 gap-1.5 text-sm font-medium"
          style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          onClick={() => setModalOpen(true)}
        >
          <Plus className="h-4 w-4" /> Add Prebuilt Habit
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow
              className="border-border hover:bg-transparent"
              style={{ backgroundColor: "rgba(209,61,61,0.06)" }}
            >
              <TableHead className="pl-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Category
              </TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Activity
              </TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Duration
              </TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Status
              </TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Action
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="py-12 text-center text-sm text-muted-foreground">
                  Loading habits...
                </TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="py-12 text-center text-sm text-muted-foreground">
                  No habits found.
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((habit) => (
                <TableRow
                  key={habit.id}
                  className="border-border transition-colors hover:bg-muted/40"
                >
                  <TableCell className="py-3.5 pl-5 text-sm font-medium text-foreground">
                    {habit.category}
                  </TableCell>
                  <TableCell className="py-3.5 text-sm text-foreground">
                    {habit.activity_name}
                  </TableCell>
                  <TableCell className="py-3.5 text-sm text-muted-foreground">
                    {habit.duration} min
                  </TableCell>
                  <TableCell className="py-3.5">
                    <span
                      className={
                        habit.status === "Active"
                          ? "text-sm font-medium text-emerald-600"
                          : "text-sm font-medium text-muted-foreground"
                      }
                    >
                      {habit.status}
                    </span>
                  </TableCell>
                  <TableCell className="py-3.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                        Action <ChevronDown className="h-3 w-3" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-44 rounded-lg">
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm"
                          onClick={() => {
                            const original = habits.find((h) => h.id === habit.id);
                            if (!original) return;
                            setEditTarget({
                              id: habit.id,
                              category: categories.find((c) => c.name === habit.category)?.id || 0,
                              category_name: habit.category_name || habit.category,
                              activity_name: habit.activity_name,
                              description: "",
                              duration: habit.duration,
                              is_active: habit.status === "Active",
                              created_at: "",
                            });
                            setEditOpen(true);
                          }}
                        >
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm"
                          onClick={() => void toggleStatus(habit.id)}
                        >
                          <ToggleLeft className="h-3.5 w-3.5 text-muted-foreground" />
                          {habit.status === "Active" ? "Deactivate" : "Activate"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive"
                          onClick={() => void handleDelete(habit.id)}
                        >
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

      <AddHabitTemplateModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        categories={categories.map((c) => ({ id: c.id, name: c.name }))}
        onSubmit={handleAdd}
      />
      <EditHabitTemplateModal
        open={editOpen}
        onOpenChange={(value) => {
          setEditOpen(value);
          if (!value) setEditTarget(null);
        }}
        categories={categories.map((c) => ({ id: c.id, name: c.name }))}
        initial={
          editTarget
            ? {
                id: editTarget.id,
                category: editTarget.category,
                activity_name: editTarget.activity_name,
                description: editTarget.description,
                duration: editTarget.duration,
                is_active: editTarget.is_active,
              }
            : null
        }
        onSubmit={handleEdit}
      />
    </div>
  );
}
