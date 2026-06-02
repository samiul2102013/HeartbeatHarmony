"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ModalError, ModalField, ModalFooter } from "./shared";

type TopicOption = {
  id: number;
  title: string;
};

type AddMaterialModalProps = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  topics: TopicOption[];
  onSubmit?: (data: { title: string; type: string; topicId: number; pdf?: File }) => void | Promise<void>;
};

export function AddMaterialModal({ open, onOpenChange, topics, onSubmit }: AddMaterialModalProps) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState("PDF");
  const [topicId, setTopicId] = useState<string>("");
  const [pdf, setPdf] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const selectedTopic = topics.find((t) => String(t.id) === topicId);

  const reset = () => {
    setTitle("");
    setType("PDF");
    setTopicId(topics[0]?.id ? String(topics[0].id) : "");
    setPdf(null);
    setError(null);
    setSaving(false);
  };

  useEffect(() => {
    if (topics.length > 0 && !topicId) {
      setTopicId(String(topics[0].id));
    }
  }, [topics, topicId]);

  const handleConfirm = async () => {
    const nextTitle = title.trim();
    if (!nextTitle) {
      setError("Material title is required.");
      return;
    }

    if (!topicId) {
      setError("Please select a topic.");
      return;
    }

    if (type === "PDF" && !pdf) {
      setError("Please upload a PDF file.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await onSubmit?.({ title: nextTitle, type, topicId: Number(topicId), pdf: pdf ?? undefined });
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create material.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(value) => { if (!value) reset(); onOpenChange(value); }}>
      <DialogContent className="sm:max-w-md rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-foreground">Add New Material</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">Create a material attached to a topic.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <ModalField label="Title">
            <Input placeholder="Enter title" value={title} onChange={(event) => setTitle(event.target.value)} className="h-11" />
          </ModalField>

          <ModalField label="Topic">
            <Select value={topicId} onValueChange={(v) => setTopicId(v ?? "")}>
              <SelectTrigger className="h-11 w-full text-sm">
                <SelectValue placeholder="Select topic" />
              </SelectTrigger>
              <SelectContent>
                {topics.map((t) => (
                  <SelectItem key={t.id} value={String(t.id)}>{t.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </ModalField>

          <ModalField label="Type">
            <Select value={type} onValueChange={(v) => { setType(v ?? "PDF"); setPdf(null); }}>
              <SelectTrigger className="h-11 text-sm">
                <SelectValue placeholder="Choose type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PDF">PDF</SelectItem>
                <SelectItem value="Video">Video</SelectItem>
                <SelectItem value="Text">Text</SelectItem>
              </SelectContent>
            </Select>
          </ModalField>

          <ModalField label={type === "PDF" ? "PDF File" : type === "Text" ? "Text Content" : "File"}>
            <Input
              type="file"
              accept={type === "PDF" ? ".pdf,application/pdf" : undefined}
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                setPdf(file);
              }}
              className="h-11"
            />
            {pdf && <p className="text-xs text-muted-foreground mt-1">Selected: {pdf.name}</p>}
          </ModalField>

          <ModalError message={error} />
        </div>

        <div className="mt-6">
          <ModalFooter onCancel={() => { reset(); onOpenChange(false); }} confirmLabel="Add Material" onConfirm={handleConfirm} loading={saving} />
        </div>
      </DialogContent>
    </Dialog>
  );
}