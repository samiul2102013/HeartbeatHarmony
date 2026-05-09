"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Camera, Eye, EyeOff, Loader2 } from "lucide-react";
import { getAdminProfile, updateAdminProfile, changeAdminPassword } from "@/lib/api/accounts/settings";

interface ProfileData {
  id?: number;
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  avatar?: string | null;
}

export default function Settings() {
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);

  const [profile, setProfile] = useState<ProfileData>({});
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);

  const [passwords, setPasswords] = useState({ current: "", next: "" });
  const [pwSaving, setPwSaving] = useState(false);
  const [pwError, setPwError] = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setProfileLoading(true);
    getAdminProfile()
      .then((data) => {
        if (!mounted) return;
        setProfile({
          id: data?.id,
          username: data?.username,
          email: data?.email ?? "",
          first_name: data?.first_name ?? "",
          last_name: data?.last_name ?? "",
          phone_number: data?.phone_number ?? "",
          avatar: data?.avatar,
        });
      })
      .catch((err) => {
        if (!mounted) return;
        setProfileError(err instanceof Error ? err.message : "Failed to load profile");
      })
      .finally(() => {
        if (mounted) setProfileLoading(false);
      });
    return () => { mounted = false; };
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setAvatarPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleSaveProfile = async () => {
    setProfileError(null);
    setProfileSuccess(null);
    setProfileSaving(true);
    try {
      const result = await updateAdminProfile({
        first_name: profile.first_name?.trim(),
        last_name: profile.last_name?.trim(),
        email: profile.email?.trim(),
        phone_number: profile.phone_number?.trim(),
        avatar: avatarFile,
      });
      setProfileSuccess("Profile updated successfully");
      setAvatarFile(null);
      setAvatarPreview(null);
      if (result?.avatar) {
        setProfile((p) => ({ ...p, avatar: result.avatar }));
      }
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setProfileSaving(false);
    }
  };

  const handleChangePassword = async () => {
    setPwError(null);
    setPwSuccess(null);
    if (!passwords.current.trim() || !passwords.next.trim()) {
      setPwError("Both fields are required");
      return;
    }
    if (passwords.next.trim().length < 6) {
      setPwError("New password must be at least 6 characters");
      return;
    }
    setPwSaving(true);
    try {
      await changeAdminPassword({
        old_password: passwords.current.trim(),
        new_password: passwords.next.trim(),
      });
      setPwSuccess("Password changed successfully");
      setPasswords({ current: "", next: "" });
    } catch (err) {
      setPwError(err instanceof Error ? err.message : "Failed to change password");
    } finally {
      setPwSaving(false);
    }
  };

  const displayName = [profile.first_name, profile.last_name].filter(Boolean).join(" ") || profile.username || "Admin User";
  const avatarUrl = profile.avatar ?? `https://api.dicebear.com/7.x/avataaars/svg?seed=${profile.username ?? "Admin"}`;

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-foreground">System Settings</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Configure global platform behavior and internal security.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">

        {/* ── Profile Card ─────────────────────────────────────── */}
        <Card className="rounded-xl border border-border bg-card shadow-sm">
          <CardContent className="p-6 space-y-5">

            {/* Avatar */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative">
                <div className="h-20 w-20 rounded-xl overflow-hidden bg-muted ring-1 ring-border">
                  <img
                    src={avatarPreview ?? avatarUrl}
                    alt={displayName}
                    className="h-full w-full object-cover"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => document.getElementById("avatar-upload")?.click()}
                  className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full flex items-center justify-center text-background shadow-sm"
                  style={{ backgroundColor: "var(--primary)" }}
                >
                  <Camera className="h-3 w-3" />
                </button>
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>
              <div className="text-center">
                <p className="text-sm font-semibold text-foreground">{displayName}</p>
                <p className="text-xs text-muted-foreground">{profile.email || "admin@aura-wellness.io"}</p>
              </div>
            </div>

            {profileLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <>
                {/* First Name */}
                <div className="space-y-1.5">
                  <Label htmlFor="firstName" className="text-sm font-medium text-foreground">First Name</Label>
                  <Input
                    id="firstName"
                    placeholder="Enter first name"
                    value={profile.first_name ?? ""}
                    onChange={(e) => setProfile((p) => ({ ...p, first_name: e.target.value }))}
                    className="h-9 text-sm"
                  />
                </div>

                {/* Last Name */}
                <div className="space-y-1.5">
                  <Label htmlFor="lastName" className="text-sm font-medium text-foreground">Last Name</Label>
                  <Input
                    id="lastName"
                    placeholder="Enter last name"
                    value={profile.last_name ?? ""}
                    onChange={(e) => setProfile((p) => ({ ...p, last_name: e.target.value }))}
                    className="h-9 text-sm"
                  />
                </div>

                {/* Email */}
                <div className="space-y-1.5">
                  <Label htmlFor="email" className="text-sm font-medium text-foreground">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={profile.email ?? ""}
                    onChange={(e) => setProfile((p) => ({ ...p, email: e.target.value }))}
                    className="h-9 text-sm"
                  />
                </div>

                {/* Phone */}
                <div className="space-y-1.5">
                  <Label htmlFor="phone" className="text-sm font-medium text-foreground">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="Enter phone number"
                    value={profile.phone_number ?? ""}
                    onChange={(e) => setProfile((p) => ({ ...p, phone_number: e.target.value }))}
                    className="h-9 text-sm"
                  />
                </div>

                {profileError && (
                  <p className="text-xs text-red-500">{profileError}</p>
                )}
                {profileSuccess && (
                  <p className="text-xs text-green-600">{profileSuccess}</p>
                )}

                <Button
                  className="w-full h-9 text-sm font-medium"
                  style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
                  onClick={handleSaveProfile}
                  disabled={profileSaving}
                >
                  {profileSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save Profile"}
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        {/* ── Security Card ─────────────────────────────────────── */}
        <Card className="rounded-xl border border-border bg-card shadow-sm">
          <CardHeader className="px-6 pt-6 pb-2">
            <h2 className="text-sm font-semibold text-foreground">Security &amp; Privacy</h2>
          </CardHeader>
          <CardContent className="px-6 pb-6 space-y-4">

            {/* Current Password */}
            <div className="space-y-1.5">
              <Label htmlFor="current-pw" className="text-sm font-medium text-foreground">Current Password</Label>
              <div className="relative">
                <Input
                  id="current-pw"
                  type={showCurrentPw ? "text" : "password"}
                  placeholder="Enter current password"
                  value={passwords.current}
                  onChange={(e) => setPasswords((p) => ({ ...p, current: e.target.value }))}
                  className="h-9 text-sm pr-9"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPw((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showCurrentPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div className="space-y-1.5">
              <Label htmlFor="new-pw" className="text-sm font-medium text-foreground">New Password</Label>
              <div className="relative">
                <Input
                  id="new-pw"
                  type={showNewPw ? "text" : "password"}
                  placeholder="Enter new password"
                  value={passwords.next}
                  onChange={(e) => setPasswords((p) => ({ ...p, next: e.target.value }))}
                  className="h-9 text-sm pr-9"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPw((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showNewPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {pwError && (
              <p className="text-xs text-red-500">{pwError}</p>
            )}
            {pwSuccess && (
              <p className="text-xs text-green-600">{pwSuccess}</p>
            )}

            <Button
              className="w-full h-9 text-sm font-medium"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
              onClick={handleChangePassword}
              disabled={pwSaving}
            >
              {pwSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Change Password"}
            </Button>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
