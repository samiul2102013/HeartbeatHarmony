"use client";

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
import { resolveUserAvatarUrl, updateUser } from "@/lib/api/accounts/users";
import { useEffect, useRef, useState } from "react";

export type UserRow = {
  id: number;
  name: string;
  username: string;
  image: string;
  email: string;
  phone: string;
  plan: "Free" | "Premium";
  status: "Active" | "Inactive";
};

type Props = {
  user: UserRow | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (updated: UserRow) => void;
};

export function EditUserDialog({ user, open, onOpenChange, onSave }: Props) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [plan, setPlan] = useState<"free" | "pro">("free");
  const [isActive, setIsActive] = useState(true);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // Populate form when user changes
  useEffect(() => {
    if (!user) return;
    const parts = user.name.split(" ");
    setFirstName(parts[0] ?? "");
    setLastName(parts.slice(1).join(" "));
    setUsername(user.username);
    setEmail(user.email);
    setPhone(user.phone === "-" ? "" : user.phone);
    setPlan(user.plan === "Premium" ? "pro" : "free");
    setIsActive(user.status === "Active");
    setAvatarFile(null);
    setAvatarPreview(user.image);
    setError(null);
  }, [user]);

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    setError(null);

    try {
      let refreshedUser;

      if (avatarFile) {
        const form = new FormData();
        form.append("first_name", firstName);
        form.append("last_name", lastName);
        form.append("username", username);
        form.append("email", email);
        form.append("phone_number", phone);
        form.append("plan", plan);
        form.append("is_active", String(isActive));
        form.append("avatar", avatarFile);
        refreshedUser = await updateUser(user.id, form);
      } else {
        refreshedUser = await updateUser(user.id, {
          first_name: firstName,
          last_name: lastName,
          username,
          email,
          phone_number: phone,
          plan,
          is_active: isActive,
        });
      }

      // PATCH already returns the updated user — no need for getUser() fallback
      if (!refreshedUser) {
        setError("Update failed: no response from server.");
        return;
      }

      const fullName = [refreshedUser.first_name, refreshedUser.last_name]
        .filter(Boolean)
        .join(" ")
        .trim();

      onSave({
        ...user,
        name: fullName || refreshedUser.username,
        username: refreshedUser.username,
        email: refreshedUser.email,
        phone: refreshedUser.phone_number || "-",
        plan: refreshedUser.plan === "pro" ? "Premium" : "Free",
        status: refreshedUser.is_active ? "Active" : "Inactive",
        image: resolveUserAvatarUrl(refreshedUser.avatar, refreshedUser.username),
      });

      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update user.");
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Edit User
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-1">
          {/* Avatar */}
          <div className="flex items-center gap-4">
            <div
              className="relative h-16 w-16 cursor-pointer overflow-hidden rounded-full bg-muted ring-2 ring-border transition-opacity hover:opacity-80"
              onClick={() => fileRef.current?.click()}
            >
              <img
                src={avatarPreview}
                alt="Avatar"
                className="h-full w-full object-cover"
                loading="lazy"
              />
            </div>
            <div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-8 text-xs"
                onClick={() => fileRef.current?.click()}
              >
                Change Photo
              </Button>
              <p className="mt-1 text-xs text-muted-foreground">
                Click avatar or button to upload
              </p>
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleAvatarChange}
            />
          </div>

          {/* Name row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">First Name</Label>
              <Input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="h-8 text-sm"
                placeholder="First name"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">Last Name</Label>
              <Input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="h-8 text-sm"
                placeholder="Last name"
              />
            </div>
          </div>

          {/* Username */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">Username</Label>
            <Input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="h-8 text-sm"
              placeholder="username"
            />
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">Email</Label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-8 text-sm"
              placeholder="email@example.com"
            />
          </div>

          {/* Phone */}
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">Phone Number</Label>
            <Input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="h-8 text-sm"
              placeholder="+880..."
            />
          </div>

          {/* Plan + Status */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">Plan</Label>
              <Select
                value={plan}
                onValueChange={(v) => setPlan(v as "free" | "pro")}
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
              <Label className="text-xs font-medium">Status</Label>
              <Select
                value={isActive ? "active" : "inactive"}
                onValueChange={(v) => setIsActive(v === "active")}
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
            onClick={() => onOpenChange(false)}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            disabled={saving}
            style={{
              backgroundColor: "var(--primary)",
              color: "var(--primary-foreground)",
            }}
          >
            {saving ? "Saving…" : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}