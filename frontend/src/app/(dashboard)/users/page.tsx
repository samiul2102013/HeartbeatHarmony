"use client";

import { AddUserModal } from "@/components/dashboard/modals/AddUserModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table, TableBody, TableCell,
  TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Dialog, DialogContent, DialogHeader,
  DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { listUsers, deleteUser, AdminUser, resolveUserAvatarUrl } from "@/lib/api/accounts/users";
import {
  ChevronDown, ChevronLeft, ChevronRight,
  Eye, Pencil, Plus, Search, Trash2,
} from "lucide-react";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";
import { EditUserDialog, type UserRow } from "./edit-user-dialog";

const ITEMS_PER_PAGE = 10;

function StatusBadge({ status }: { status: UserRow["status"] }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
      status === "Active" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
    }`}>
      {status}
    </span>
  );
}

function PlanBadge({ plan }: { plan: UserRow["plan"] }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
      plan === "Premium" ? "bg-orange-100 text-orange-600" : "bg-muted text-muted-foreground"
    }`}>
      {plan}
    </span>
  );
}

function mapUser(user: AdminUser): UserRow {
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ").trim();
  return {
    id: user.id,
    name: fullName || user.institute_name || user.username,
    username: user.username,
    institute_name: user.institute_name,
    image: resolveUserAvatarUrl(user.avatar, user.username),
    email: user.email,
    phone: user.phone_number || "-",
    plan: user.plan === "pro" ? "Premium" : "Free",
    status: user.is_active ? "Active" : "Inactive",
  };
}

function ViewUserDialog({ user, open, onOpenChange }: {
  user: UserRow | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  if (!user) return null;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">User Details</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col items-center gap-3 py-2">
          <div className="relative h-20 w-20 overflow-hidden rounded-full bg-muted ring-2 ring-border">
            <Image
              src={user.image}
              alt={user.name || user.email || "User avatar"}
              fill
              className="object-cover"
              unoptimized
            />
          </div>
          <div className="text-center">
            <p className="text-base font-semibold">{user.name}</p>
            <p className="text-xs text-muted-foreground">@{user.institute_name || user.username}</p>
            <p className="text-sm text-muted-foreground">{user.email}</p>
          </div>
        </div>
        <div className="space-y-2 rounded-lg border border-border bg-muted/30 p-3 text-sm">
          {[
            ["Phone", user.phone],
            ["Plan", user.plan],
            ["Status", user.status],
          ].map(([label, value]) => (
            <div key={label} className="flex items-center justify-between">
              <span className="text-muted-foreground">{label}</span>
              <span className="font-medium">{value}</span>
            </div>
          ))}
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function UserManagement() {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editUser, setEditUser] = useState<UserRow | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [viewUser, setViewUser] = useState<UserRow | null>(null);
  const [viewOpen, setViewOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<UserRow | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  function normalizeUsersResponse(res: any): AdminUser[] {
    const source = res?.data ?? res?.results ?? res?.result ?? res ?? [];
    return Array.isArray(source) ? source : (source?.results ?? []);
  }

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await listUsers();
      const normalizedUsers = normalizeUsersResponse(res);
      setUsers(normalizedUsers.map(mapUser));
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unable to load users";
      setError(`❌ ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await listUsers();
        const normalizedUsers = normalizeUsersResponse(res);
        if (mounted) setUsers(normalizedUsers.map(mapUser));
      } catch (err) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Unable to load users";
          setError(`❌ ${msg}`);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };
    void load();
    return () => { mounted = false; };
  }, []);

  useEffect(() => { setCurrentPage(1); }, [searchTerm]);

  const filteredUsers = useMemo(
    () => users.filter(
      (u) =>
        (u.name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
        (u.email || "").toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [searchTerm, users]
  );

  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / ITEMS_PER_PAGE));
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedUsers = filteredUsers.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  const pageNumbers = useMemo(() => {
    const pages: (number | "…")[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push("…");
      for (
        let i = Math.max(2, currentPage - 1);
        i <= Math.min(totalPages - 1, currentPage + 1);
        i++
      ) pages.push(i);
      if (currentPage < totalPages - 2) pages.push("…");
      pages.push(totalPages);
    }
    return pages;
  }, [currentPage, totalPages]);

  // Optimistic update then re-fetch to sync with server
  const handleEditSave = (updated: UserRow) => {
    setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
    void loadUsers();
  };

  const handleUserAdded = (newUser: AdminUser) => {
    setUsers((prev) => [mapUser(newUser), ...prev]);
    void loadUsers();
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteUser(deleteTarget.id);
      setUsers((prev) => prev.filter((u) => u.id !== deleteTarget.id));
      setDeleteOpen(false);
      setDeleteTarget(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete user.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">User Management</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Manage and monitor your community of {users.length} users.
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
            placeholder="Search by name or email…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="h-9 pl-9 text-sm"
          />
        </div>
        <Button
          className="h-9 gap-1.5 text-sm font-medium"
          style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          onClick={() => setAddModalOpen(true)}
        >
          <Plus className="h-4 w-4" /> Add Users
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm min-h-[520px]">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
              {["Name", "Image", "Email", "Phone Number", "Plan", "Status", "Action"].map((h) => (
                <TableHead key={h} className="text-xs font-semibold uppercase tracking-wide text-muted-foreground first:pl-5">
                  {h}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="py-12 text-center text-sm text-muted-foreground">
                  Loading users…
                </TableCell>
              </TableRow>
            ) : paginatedUsers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="py-12 text-center text-sm text-muted-foreground">
                  No users found.
                </TableCell>
              </TableRow>
            ) : (
              paginatedUsers.map((user) => (
                <TableRow key={user.id} className="border-border transition-colors hover:bg-muted/40">
                  <TableCell className="py-3.5 pl-5">
                    <span className="text-sm font-medium text-foreground">
                      {user.name || "—"}
                    </span>
                  </TableCell>

                  <TableCell className="py-3.5">
                    <div className="relative h-9 w-9 overflow-hidden rounded-full bg-muted ring-1 ring-border">
                      <Image
                        src={user.image}
                        alt={user.name || user.email || "User avatar"}
                        fill
                        className="object-cover"
                        unoptimized
                        loading="eager"
                      />
                    </div>
                  </TableCell>

                  <TableCell className="py-3.5">
                    <span className="text-sm text-muted-foreground">{user.email}</span>
                  </TableCell>

                  <TableCell className="py-3.5">
                    <span className="text-sm text-muted-foreground">{user.phone}</span>
                  </TableCell>

                  <TableCell className="py-3.5">
                    <PlanBadge plan={user.plan} />
                  </TableCell>

                  <TableCell className="py-3.5">
                    <StatusBadge status={user.status} />
                  </TableCell>

                  <TableCell className="py-3.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                        Action <ChevronDown className="h-3 w-3" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-44 rounded-lg">
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm"
                          onClick={() => { setViewUser(user); setViewOpen(true); }}
                        >
                          <Eye className="h-3.5 w-3.5 text-muted-foreground" /> View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm"
                          onClick={() => { setEditUser(user); setEditOpen(true); }}
                        >
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive"
                          onClick={() => { setDeleteTarget(user); setDeleteOpen(true); }}
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

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {filteredUsers.length === 0
            ? "No results"
            : `Showing ${startIndex + 1}–${Math.min(startIndex + ITEMS_PER_PAGE, filteredUsers.length)} of ${filteredUsers.length}`}
        </p>
        <div className="flex items-center gap-1 min-w-[300px] justify-end">
          <Button variant="outline" size="icon" className="h-8 w-8"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}>
            <ChevronLeft className="h-4 w-4" />
          </Button>

          {pageNumbers.map((page, i) =>
            page === "…" ? (
              <span key={`ellipsis-${i}`} className="flex h-8 w-8 items-center justify-center text-xs text-muted-foreground">…</span>
            ) : (
              <Button key={page} variant={currentPage === page ? "default" : "outline"}
                size="icon" className="h-8 w-8 text-xs"
                style={currentPage === page ? { backgroundColor: "var(--primary)", color: "var(--primary-foreground)" } : {}}
                onClick={() => setCurrentPage(page as number)}>
                {page}
              </Button>
            )
          )}

          <Button variant="outline" size="icon" className="h-8 w-8"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <AddUserModal
        open={addModalOpen}
        onOpenChange={setAddModalOpen}
        onUserCreated={handleUserAdded}
      />

      <EditUserDialog
        user={editUser}
        open={editOpen}
        onOpenChange={setEditOpen}
        onSave={handleEditSave}
      />

      <ViewUserDialog
        user={viewUser}
        open={viewOpen}
        onOpenChange={setViewOpen}
      />

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-base font-semibold">Delete user?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            This will permanently delete{" "}
            <strong className="text-foreground">{deleteTarget?.name}</strong>.
            This action cannot be undone.
          </p>
          <DialogFooter className="gap-2">
            <Button variant="outline" size="sm"
              onClick={() => { setDeleteTarget(null); setDeleteOpen(false); }}
              disabled={deleting}>
              Cancel
            </Button>
            <Button size="sm"
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={() => void handleDeleteConfirm()}
              disabled={deleting}>
              {deleting ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}