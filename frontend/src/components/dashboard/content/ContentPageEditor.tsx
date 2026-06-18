"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Pencil } from "lucide-react";
import { ContentEditor } from "@/components/dashboard/content/ContentEditor";
import { ContentPageData } from "@/lib/api/content/content";

interface ContentPageEditorProps {
  title: string;
  description: string;
  fetchFn: () => Promise<ContentPageData>;
  updateFn: (data: Partial<ContentPageData>) => Promise<ContentPageData>;
}

export function ContentPageEditor({ title, description, fetchFn, updateFn }: ContentPageEditorProps) {
  const [content, setContent] = useState("");
  const [pageTitle, setPageTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchFn();
      setContent(data.content);
      setPageTitle(data.title);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load content");
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async () => {
    setError(null);
    setSuccess(null);
    setSaving(true);
    try {
      await updateFn({ title: pageTitle, content });
      setSuccess("Content saved successfully");
      setEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save content");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditing(false);
    load();
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground mt-0.5">{description}</p>
      </div>

      <Card className="rounded-xl border border-border bg-card shadow-sm">
        <CardContent className="p-6 space-y-4">
          {editing ? (
            <>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground">Page Title</label>
                <input
                  type="text"
                  value={pageTitle}
                  onChange={(e) => setPageTitle(e.target.value)}
                  className="flex h-9 w-full rounded-lg border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground">Content</label>
                <ContentEditor value={content} onChange={setContent} />
              </div>

              {error && <p className="text-xs text-red-500">{error}</p>}
              {success && <p className="text-xs text-green-600">{success}</p>}

              <div className="flex gap-3">
                <Button
                  className="h-9 text-sm font-medium"
                  style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save Content"}
                </Button>
                <Button
                  variant="outline"
                  className="h-9 text-sm font-medium"
                  onClick={handleCancel}
                  disabled={saving}
                >
                  Cancel
                </Button>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-foreground">{pageTitle}</h2>
                <Button
                  className="h-9 text-sm font-medium gap-2"
                  style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
                  onClick={() => setEditing(true)}
                >
                  <Pencil className="h-4 w-4" />
                  Edit
                </Button>
              </div>

              <div
                className="prose prose-sm max-w-none text-muted-foreground"
                dangerouslySetInnerHTML={{ __html: content }}
              />

              {error && <p className="text-xs text-red-500">{error}</p>}
              {success && <p className="text-xs text-green-600">{success}</p>}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
