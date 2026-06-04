"use client";

import { AddHabitMaterialModal } from "@/components/dashboard/modals/AddHabitMaterialModal";
import { EditHabitMaterialModal } from "@/components/dashboard/modals/EditHabitMaterialModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ChevronDown,
  Pencil,
  Plus,
  Search,
  Trash2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AdminHabit,
  AdminHabitMaterial,
  HabitTemplate,
  createHabitMaterial,
  removeHabitMaterial,
  editHabitMaterial,
  listHabitMaterials,
  listHabitTemplates,
  listHabits,
} from "@/lib/index";

type MaterialRow = {
  id: number;
  title: string;
  habit: string;
  type: "PDF" | "Video";
  date: string;
  status: "Active" | "Inactive";
};

const TYPE_COLORS: Record<MaterialRow["type"], string> = {
  PDF: "bg-red-50 text-red-600",
  Video: "bg-blue-50 text-blue-600",
};

function normalizeResponse<T>(res: unknown): T[] {
  if (!res) return [];
  if (Array.isArray(res)) return res as T[];
  const obj = res as Record<string, unknown>;
  if (Array.isArray(obj.results)) return obj.results as T[];
  if (Array.isArray(obj.data)) return obj.data as T[];
  return [];
}

function mapType(type: string | null | undefined): MaterialRow["type"] {
  const normalized = (type || "pdf").toLowerCase();
  if (normalized === "video") return "Video";
  return "PDF";
}

function mapMaterial(material: AdminHabitMaterial): MaterialRow {
  return {
    id: material.id,
    title: material.title,
    habit: material.habit_title || "Unassigned habit",
    type: mapType(material.material_type),
    date: new Date(material.created_at).toLocaleDateString(),
    status: material.is_active ? "Active" : "Inactive",
  };
}

function buildFormData(data: {
  habit_template: number;
  title: string;
  material_type: string;
  file?: File;
  video_url?: string;
}) {
  const formData = new FormData();
  formData.append("habit_template", String(data.habit_template));
  formData.append("title", data.title);
  formData.append("description", "");
  formData.append("material_type", data.material_type);
  formData.append("video_url", data.video_url ?? "");
  formData.append("is_active", "true");
  if (data.file) {
    formData.append("file", data.file);
  }
  return formData;
}

export default function HabitMaterialsPage() {
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingMaterial, setEditingMaterial] = useState<MaterialRow | null>(null);
  const [rawMaterials, setRawMaterials] = useState<AdminHabitMaterial[]>([]);
  const [materials, setMaterials] = useState<MaterialRow[]>([]);
  const [habits, setHabits] = useState<(HabitTemplate | AdminHabit)[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        const [materialsResponse, habitsResponse, userHabitsResponse] = await Promise.all([listHabitMaterials(), listHabitTemplates(), listHabits()]);
        if (!mounted) return;
        const raw = normalizeResponse<AdminHabitMaterial>(materialsResponse);
        setRawMaterials(raw);
        setMaterials(raw.map(mapMaterial));
        const templates = normalizeResponse<HabitTemplate>(habitsResponse);
        const userHabits = normalizeResponse<AdminHabit>(userHabitsResponse);
        setHabits([...templates, ...userHabits]);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load habit materials");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void loadData();

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(
    () => materials.filter((material) => (material.title || "").toLowerCase().includes(search.toLowerCase()) || (material.habit || "").toLowerCase().includes(search.toLowerCase())),
    [materials, search]
  );

  const handleCreate = async (data: {
    habit_template: number;
    title: string;
    material_type: string;
    file?: File;
    video_url?: string;
  }) => {
    const response = await createHabitMaterial(buildFormData(data));
    const created = (response as any)?.data ?? response;
    setMaterials((prev) => [...prev, mapMaterial(created as AdminHabitMaterial)]);
    setRawMaterials((prev) => [...prev, created as AdminHabitMaterial]);
  };

  const handleEdit = async (data: {
    id: number;
    title: string;
    material_type: string;
    file?: File;
    video_url?: string;
  }) => {
    try {
      setError(null);
      const raw = rawMaterials.find((item) => item.id === data.id);
      const formData = new FormData();
      if (raw) formData.append("habit", String(raw.habit));
      formData.append("title", data.title);
      formData.append("description", "");
      formData.append("material_type", data.material_type);
      formData.append("video_url", data.video_url ?? "");
      formData.append("is_active", "true");
      if (data.file) formData.append("file", data.file);
      const response = await editHabitMaterial(data.id, formData);
      const updated = (response as any)?.data ?? response;
      setRawMaterials((prev) => prev.map((item) => (item.id === data.id ? (updated as AdminHabitMaterial) : item)));
      setMaterials((prev) => prev.map((item) => (item.id === data.id ? mapMaterial(updated as AdminHabitMaterial) : item)));
      setEditingMaterial(null);
      setEditModalOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update habit material");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this habit material?")) return;
    try {
      setError(null);
      await removeHabitMaterial(id);
      setMaterials((prev) => prev.filter((item) => item.id !== id));
      setRawMaterials((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete habit material");
    }
  };

  const habitOptions = habits.map((habit) => ({
    id: habit.id,
    activity_name: habit.activity_name,
  }));

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Material Under Habit</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Attach PDFs, videos, audio, and text resources to habits.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="h-9 pl-9 text-sm" />
        </div>
        <Button className="h-9 gap-1.5 text-sm font-medium" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => setModalOpen(true)}>
          <Plus className="h-4 w-4" /> Add Material
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
              <TableHead className="pl-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Habit</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Title</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Type</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Date</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Status</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="py-12 text-center text-sm text-muted-foreground">Loading habit materials...</TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="py-12 text-center text-sm text-muted-foreground">No habit materials found.</TableCell>
              </TableRow>
            ) : (
              filtered.map((material) => (
                <TableRow key={material.id} className="border-border transition-colors hover:bg-muted/40">
                  <TableCell className="py-3.5 pl-5 text-sm font-medium text-foreground">{material.habit}</TableCell>
                  <TableCell className="py-3.5 text-sm text-foreground">{material.title}</TableCell>
                  <TableCell className="py-3.5">
                    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${TYPE_COLORS[material.type]}`}>
                      {material.type}
                    </span>
                  </TableCell>
                  <TableCell className="py-3.5 text-sm text-muted-foreground">{material.date}</TableCell>
                  <TableCell className="py-3.5 text-sm font-medium">{material.status}</TableCell>
                  <TableCell className="py-3.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                        Action <ChevronDown className="h-3 w-3" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-44 rounded-lg">
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm" onClick={() => { setEditingMaterial(material); setEditModalOpen(true); }}>
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive" onClick={() => void handleDelete(material.id)}>
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

      <AddHabitMaterialModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        habits={habitOptions}
        onSubmit={handleCreate}
      />

      <EditHabitMaterialModal
        open={editModalOpen}
        onOpenChange={(value) => {
          setEditModalOpen(value);
          if (!value) setEditingMaterial(null);
        }}
        habits={habitOptions}
        material={editingMaterial ? (() => {
          const raw = rawMaterials.find((item) => item.id === editingMaterial.id);
          return {
            id: editingMaterial.id,
            title: editingMaterial.title,
            material_type: editingMaterial.type,
            habitId: raw?.habit ?? 0,
            habitTitle: raw?.habit_title ?? editingMaterial.habit,
          };
        })() : null}
        onSubmit={handleEdit}
      />
    </div>
  );
}
