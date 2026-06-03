"use client";

import { AddMaterialModal } from "@/components/dashboard/modals/AddMaterialModal";
import { EditMaterialModal } from "@/components/dashboard/modals/EditMaterialModal";
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
import { AdminMaterial, StudyTopic, createMaterial, deleteMaterial, listMaterials, listTopics, updateMaterial } from "@/lib/index";
import { ChevronDown, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type MaterialRow = {
  id: number;
  topic: string;
  title: string;
  type: "PDF" | "Video" | "Text";
  date: string;
};

const TYPE_COLORS: Record<MaterialRow["type"], string> = {
  PDF: "bg-red-50 text-red-600",
  Video: "bg-blue-50 text-blue-600",
  Text: "bg-green-50 text-green-600",
};

function mapType(type: string | null | undefined): MaterialRow["type"] {
  if (!type) return "PDF";
  const normalized = type.toLowerCase();
  if (normalized === "video") return "Video";
  if (normalized === "text") return "Text";
  return "PDF";
}

function mapMaterial(material: AdminMaterial): MaterialRow {
  return {
    id: material.id,
    topic: material.topic_title || "Uncategorized",
    title: material.title,
    type: mapType(material.material_type),
    date: new Date(material.created_at).toLocaleDateString(),
  };
}

export default function StudyMaterials() {
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingMaterial, setEditingMaterial] = useState<MaterialRow | null>(null);
  const [rawMaterials, setRawMaterials] = useState<AdminMaterial[]>([]);
  const [materials, setMaterials] = useState<MaterialRow[]>([]);
  const [topics, setTopics] = useState<StudyTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function normalizeResponse<T>(res: any): T[] {
    const source = res?.data ?? res?.results ?? res?.result ?? res ?? [];
    return Array.isArray(source) ? source : (source?.results ?? []);
  }

  useEffect(() => {
    let mounted = true;

    const loadMaterials = async () => {
      try {
        setLoading(true);
        const [materialsResponse, topicsResponse] = await Promise.all([listMaterials(), listTopics()]);
        if (!mounted) return;
        const rawMats = normalizeResponse<AdminMaterial>(materialsResponse);
        setRawMaterials(rawMats);
        setMaterials(rawMats.map(mapMaterial));
        setTopics(normalizeResponse<StudyTopic>(topicsResponse));
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load study materials");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void loadMaterials();

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(
    () => materials.filter((material) => (material.title || "").toLowerCase().includes(search.toLowerCase())),
    [materials, search]
  );

  const handleCreateMaterial = async (data: { title: string; type: string; topicId: number; pdf?: File }) => {
    if (!data.topicId) {
      setError("No study topic selected for this material");
      return;
    }

    try {
      setError(null);
      const formData = new FormData();
      formData.append("topic", String(data.topicId));
      formData.append("title", data.title);
      formData.append("description", "");
      formData.append("material_type", (data.type || "PDF").toLowerCase());
      formData.append("content", "");
      formData.append("video_url", "");
      formData.append("is_active", "true");
      if (data.pdf) {
        formData.append("pdf", data.pdf);
      }

      const response = await createMaterial(formData);
      const created = (response as any)?.data ?? response;
      setMaterials((prev) => [...prev, mapMaterial(created)]);
      setModalOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create material");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this material?")) return;
    try {
      await deleteMaterial(id);
      setMaterials((prev) => prev.filter((material) => material.id !== id));
      setRawMaterials((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete material");
    }
  };

  const handleEditMaterial = async (data: { id: number; title: string; type: string; topicId: number; pdf?: File }) => {
    try {
      setError(null);
      const formData = new FormData();
      formData.append("topic", String(data.topicId));
      formData.append("title", data.title);
      formData.append("description", "");
      formData.append("material_type", (data.type || "PDF").toLowerCase());
      formData.append("content", "");
      formData.append("video_url", "");
      formData.append("is_active", "true");
      if (data.pdf) {
        formData.append("pdf", data.pdf);
      }

      const response = await updateMaterial(data.id, formData);
      const updated = (response as any)?.data ?? response;
      setRawMaterials((prev) => prev.map((m) => (m.id === data.id ? (updated as AdminMaterial) : m)));
      setMaterials((prev) => prev.map((m) => (m.id === data.id ? mapMaterial(updated as AdminMaterial) : m)));
      setEditModalOpen(false);
      setEditingMaterial(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update material");
      throw err;
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Study Materials</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Upload and manage educational resources for users.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="h-9 pl-9 text-sm" />
        </div>
        <Button className="h-9 gap-1.5 text-sm font-medium" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => setModalOpen(true)}>
          <Plus className="h-4 w-4" /> Add New Material
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
              <TableHead className="pl-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Topic</TableHead>
              <TableHead className="pl-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Title</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Type</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Date</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="py-12 text-center text-sm text-muted-foreground">Loading materials...</TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="py-12 text-center text-sm text-muted-foreground">No materials found.</TableCell>
              </TableRow>
            ) : (
              filtered.map((material) => (
                <TableRow key={material.id} className="border-border transition-colors hover:bg-muted/40">
                  <TableCell className="py-3.5 pl-5 text-sm text-muted-foreground">{material.topic}</TableCell>
                  <TableCell className="py-3.5 text-sm font-medium text-foreground">{material.title}</TableCell>
                  <TableCell className="py-3.5">
                    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${TYPE_COLORS[material.type]}`}>
                      {material.type}
                    </span>
                  </TableCell>
                  <TableCell className="py-3.5 text-sm text-muted-foreground">{material.date}</TableCell>
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
      <AddMaterialModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        topics={topics.map((t) => ({ id: t.id, title: (t as any).title || (t as any).name || "Untitled" }))}
        onSubmit={handleCreateMaterial}
      />
      <EditMaterialModal
        open={editModalOpen}
        onOpenChange={(v) => { if (!v) setEditingMaterial(null); setEditModalOpen(v); }}
        topics={topics.map((t) => ({ id: t.id, title: (t as any).title || (t as any).name || "Untitled" }))}
        material={editingMaterial ? (() => { const raw = rawMaterials.find((m) => m.id === editingMaterial.id); return { id: editingMaterial.id, title: editingMaterial.title, type: editingMaterial.type, topicId: raw?.topic ?? 0, topicTitle: raw?.topic_title ?? "" }; })() : null}
        onSubmit={handleEditMaterial}
      />
    </div>
  );
}
