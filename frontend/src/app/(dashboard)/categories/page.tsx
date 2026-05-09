"use client";

import { AddCategoryModal } from "@/components/dashboard/modals/AddCategoryModal";
import { EditCategoryModal } from "@/components/dashboard/modals/EditCategoryModal";
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
  AdminCategory,
  createCategory,
  deleteCategory,
  listCategories,
  updateCategory,
} from "@/lib/index";
import { ChevronDown, Pencil, Plus, Search, ToggleLeft, Trash2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type CategoryRow = {
  id: number;
  name: string;
  status: "Active" | "Inactive";
};

function mapCategory(category: AdminCategory): CategoryRow {
  return {
    id: category.id,
    name: category.name ?? "",
    status: category.is_active ? "Active" : "Inactive",
  };
}

function normalizeResponse<T>(res: unknown): T[] {
  if (!res) return [];
  if (Array.isArray(res)) return res as T[];
  const obj = res as Record<string, unknown>;
  if (Array.isArray(obj.results)) return obj.results as T[];
  if (Array.isArray(obj.data)) return obj.data as T[];
  if (Array.isArray(obj.result)) return obj.result as T[];
  if (typeof obj.id === "number") return [obj as T];
  return [];
}

export default function CategoriesPage() {
  const [search, setSearch] = useState("");
  const [categories, setCategories] = useState<CategoryRow[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<CategoryRow | null>(null);

  // KEY CHANGE: loadCategories is now a stable useCallback so any handler can call it
  const loadCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listCategories();
      setCategories(normalizeResponse<AdminCategory>(response).map(mapCategory));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load categories");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load on mount
  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  const filtered = useMemo(
    () =>
      categories.filter((category) =>
        (category.name ?? "").toLowerCase().includes((search ?? "").toLowerCase())
      ),
    [categories, search]
  );

  // After every mutation: await the API call, then re-fetch the full list
  const handleAddCategory = async (data: { name: string }) => {
    await createCategory({ name: data.name, icon: "🌿", is_active: true });
    await loadCategories();
  };

  const handleEditCategory = async (data: { name: string; is_active: boolean }) => {
    if (!editTarget) throw new Error("Select a category to edit.");
    await updateCategory(editTarget.id, {
      name: data.name.trim(),
      is_active: data.is_active,
      icon: "🌿",
    });
    setEditTarget(null);
    await loadCategories();
  };

  const toggleStatus = async (id: number) => {
    const current = categories.find((category) => category.id === id);
    if (!current) return;
    try {
      setError(null);
      await updateCategory(id, { is_active: current.status !== "Active" });
      await loadCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update category status");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setError(null);
      await deleteCategory(id);
      await loadCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete category");
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Categories</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Organize habits and activities by category.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="h-9 pl-9 text-sm"
          />
        </div>
        <Button
          className="h-9 gap-1.5 text-sm font-medium"
          style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          onClick={() => setModalOpen(true)}
        >
          <Plus className="h-4 w-4" /> Add New Category
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
                Name
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
                <TableCell colSpan={3} className="py-12 text-center text-sm text-muted-foreground">
                  Loading categories...
                </TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="py-12 text-center text-sm text-muted-foreground">
                  No categories found.
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((category) => (
                <TableRow
                  key={category.id}
                  className="border-border transition-colors hover:bg-muted/40"
                >
                  <TableCell className="py-3.5 pl-5 text-sm font-medium text-foreground">
                    {category.name}
                  </TableCell>
                  <TableCell className="py-3.5">
                    <span
                      className={
                        category.status === "Active"
                          ? "text-sm font-medium text-emerald-600"
                          : "text-sm font-medium text-muted-foreground"
                      }
                    >
                      {category.status}
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
                            setEditTarget(category);
                            setEditOpen(true);
                          }}
                        >
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm"
                          onClick={() => void toggleStatus(category.id)}
                        >
                          <ToggleLeft className="h-3.5 w-3.5 text-muted-foreground" />
                          {category.status === "Active" ? "Deactivate" : "Activate"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive"
                          onClick={() => void handleDelete(category.id)}
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

      <AddCategoryModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        onSubmit={handleAddCategory}
      />
      <EditCategoryModal
        open={editOpen}
        onOpenChange={(value) => {
          setEditOpen(value);
          if (!value) setEditTarget(null);
        }}
        initial={editTarget ? { name: editTarget.name, status: editTarget.status } : null}
        onSubmit={handleEditCategory}
      />
    </div>
  );
}
