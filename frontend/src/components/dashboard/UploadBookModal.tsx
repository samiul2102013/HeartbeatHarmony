import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

interface UploadBookModalProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSubmit?: (data: { name: string; date: string }) => void;
}

export function UploadBookModal({ open, onOpenChange, onSubmit }: UploadBookModalProps) {
  const [name, setName] = useState("");
  const [date, setDate] = useState("");

  const reset = () => {
    setName("");
    setDate("");
  };

  const handleConfirm = () => {
    if (!name.trim() || !date) return;
    onSubmit?.({ name: name.trim(), date });
    reset();
    onOpenChange(false);
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) reset();
        onOpenChange(v);
      }}
    >
      <DialogContent className="sm:max-w-2xl rounded-2xl p-6 gap-0">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-3xl font-bold text-foreground">Upload Book</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            Drag and drop your files here
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-sm font-semibold text-foreground">Subject Name</Label>
              <Input
                placeholder="Enter title"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="h-11"
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-sm font-semibold text-foreground">Date</Label>
              <Input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="h-11"
              />
            </div>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <Button
            type="button"
            variant="outline"
            className="flex-1 h-11 text-sm font-medium"
            onClick={() => {
              reset();
              onOpenChange(false);
            }}
          >
            Cancel
          </Button>
          <Button
            type="button"
            className="flex-1 h-11 text-sm font-medium"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            onClick={handleConfirm}
          >
            Upload
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}