"use client";

import { UploadBookModal } from "@/components/dashboard/modals/UploadBookModal";
import { EditSubjectModal } from "@/components/dashboard/modals/EditSubjectModal";
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
import { createTopic, deleteTopic, listTopics, StudyTopic, updateTopic } from "@/lib/index";
import { ChevronDown, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type SubjectUpload = {
  id: number;
  name: string;
  date: string;
};

function mapTopic(topic: StudyTopic): SubjectUpload {
  return {
    id: topic.id,
    name: topic.title || topic.name || "Untitled",
    date: "-",
  };
}

export default function SubjectUploadsPage() {
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<SubjectUpload | null>(null);
  const [items, setItems] = useState<SubjectUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadTopics = async () => {
      try {
        setLoading(true);
        const data = await listTopics();
        if (!mounted) return;
        setItems((Array.isArray(data) ? data : []).map(mapTopic));
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load subject uploads");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void loadTopics();

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(
    () => items.filter((item) => (item.name || "").toLowerCase().includes(search.toLowerCase())),
    [items, search]
  );

  const handleCreateTopic = async (data: { name: string; date: string }) => {
    try {
      const created = await createTopic({ title: data.name, description: "" });
      setItems((prev) => [...prev, mapTopic(created as StudyTopic)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create subject");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this subject?")) return;
    try {
      await deleteTopic(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete subject");
    }
  };

  const handleEditSubject = async (data: { id: number; name: string }) => {
    try {
      const updated = await updateTopic(data.id, { title: data.name, description: "" });
      setItems((prev) => prev.map((item) => (item.id === data.id ? mapTopic(updated as StudyTopic) : item)));
      setEditModalOpen(false);
      setEditingSubject(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update subject");
      throw err;
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Subject Uploads</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Upload and manage educational resources for users.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} className="h-9 pl-9 text-sm" />
        </div>
        <Button className="h-9 gap-1.5 text-sm font-medium" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }} onClick={() => setModalOpen(true)}>
          <Plus className="h-4 w-4" /> Upload Book
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
              <TableHead className="pl-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Subject Name</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Date</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={3} className="py-12 text-center text-sm text-muted-foreground">Loading subject uploads...</TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="py-12 text-center text-sm text-muted-foreground">No subject uploads found.</TableCell>
              </TableRow>
            ) : (
              filtered.map((item) => (
                <TableRow key={item.id} className="border-border transition-colors hover:bg-muted/40">
                  <TableCell className="py-3.5 pl-5 text-sm font-medium text-foreground">{item.name}</TableCell>
                  <TableCell className="py-3.5 text-sm text-muted-foreground">{item.date}</TableCell>
                  <TableCell className="py-3.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                        Action <ChevronDown className="h-3 w-3" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-44 rounded-lg">
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm" onClick={() => { setEditingSubject(item); setEditModalOpen(true); }}>
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive" onClick={() => void handleDelete(item.id)}><Trash2 className="h-3.5 w-3.5" /> Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <UploadBookModal open={modalOpen} onOpenChange={setModalOpen} onSubmit={handleCreateTopic} />
      <EditSubjectModal
        open={editModalOpen}
        onOpenChange={(v) => { if (!v) setEditingSubject(null); setEditModalOpen(v); }}
        subject={editingSubject}
        onSubmit={handleEditSubject}
      />
    </div>
  );
}
