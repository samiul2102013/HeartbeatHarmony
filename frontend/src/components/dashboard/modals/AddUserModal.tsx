"use client";

// src/components/dashboard/modals/AddUserModal.tsx 
// Replace your existing AddUserModal with this

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { createUser, AdminUser } from "@/lib/api/accounts/users";
import { useState } from "react";

type Props = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onUserCreated?: (user: AdminUser) => void;
};

const DEFAULT_FORM = {
  username: "",
  email: "",
  first_name: "",
  last_name: "",
  phone_number: "",
  password: "",
  plan: "free" as "free" | "pro",
  role: "user" as "admin" | "user",
  is_active: true,
};

export function AddUserModal({ open, onOpenChange, onUserCreated }: Props) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (field: keyof typeof DEFAULT_FORM, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const reset = () => {
    setForm(DEFAULT_FORM);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!form.username.trim() || !form.email.trim()) {
      setError("Username and email are required.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const newUser = await createUser({
        username: form.username.trim(),
        email: form.email.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        phone_number: form.phone_number.trim(),
        password: form.password.trim() || "HeartBeat123!",
        plan: form.plan,
        role: form.role,
        is_active: form.is_active,
      });

      onUserCreated?.(newUser);
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create user.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) reset();
        onOpenChange(v);
      }}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Add New User
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-1">
          {/* Name row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">First Name</Label>
              <Input
                value={form.first_name}
                onChange={(e) => set("first_name", e.target.value)}
                className="h-8 text-sm"
                placeholder="First name"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">Last Name</Label>
              <Input
                value={form.last_name}
                onChange={(e) => set("last_name", e.target.value)}
                className="h-8 text-sm"
                placeholder="Last name"
              />
            </div>
          </div>

          {/* Username */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">
              Username <span className="text-destructive">*</span>
            </Label>
            <Input
              value={form.username}
              onChange={(e) => set("username", e.target.value)}
              className="h-8 text-sm"
              placeholder="username"
            />
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">
              Email <span className="text-destructive">*</span>
            </Label>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => set("email", e.target.value)}
              className="h-8 text-sm"
              placeholder="email@example.com"
            />
          </div>

          {/* Phone */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">Phone Number</Label>
            <Input
              value={form.phone_number}
              onChange={(e) => set("phone_number", e.target.value)}
              className="h-8 text-sm"
              placeholder="+880..."
            />
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">
              Password{" "}
              <span className="text-muted-foreground font-normal">
                (default: HeartBeat123!)
              </span>
            </Label>
            <Input
              type="password"
              value={form.password}
              onChange={(e) => set("password", e.target.value)}
              className="h-8 text-sm"
              placeholder="Leave blank for default"
            />
          </div>

          {/* Plan + Role */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">Plan</Label>
              <Select
                value={form.plan}
                onValueChange={(v) => set("plan", v ?? "free")}
              >
                <SelectTrigger className="h-8 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="free">Free</SelectItem>
                  <SelectItem value="pro">Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs font-medium">Role</Label>
              <Select
                value={form.role}
                onValueChange={(v) => set("role", v ?? "user")}
              >
                <SelectTrigger className="h-8 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Status */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">Status</Label>
            <Select
              value={form.is_active ? "active" : "inactive"}
              onValueChange={(v) => set("is_active", v === "active")}
            >
              <SelectTrigger className="h-8 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {error && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">
              {error}
            </p>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              reset();
              onOpenChange(false);
            }}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleSubmit}
            disabled={saving}
            style={{
              backgroundColor: "var(--primary)",
              color: "var(--primary-foreground)",
            }}
          >
            {saving ? "Creating…" : "Create User"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}