"use client";

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
import { deleteCheckin, AdminCheckIn } from "@/lib/index";
import { useCheckins, useDeleteCheckin } from "@/lib/api/checkins/hooks";
import { CalendarDays, ChevronDown, Eye, Pencil, Search, Trash2 } from "lucide-react";
import ViewCheckInDialog from "./veiw-checksin-dialog";
import { useEffect, useMemo, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type CheckInRow = {
  id: number;
  name: string;
  date: string;
  mood: string;
  score: string;
};

const ITEMS_PER_PAGE = 10;

function mapCheckIn(checkIn: AdminCheckIn): CheckInRow {
  return {
    id: checkIn.id,
    name: checkIn.user_username,
    date: new Date(checkIn.created_at).toLocaleDateString(),
    mood: checkIn.mood_name,
    score: `${Math.round(checkIn.heart_balance_score)}%`,
  };
}

const MOOD_COLORS: Record<string, string> = {
  Joyful: "text-emerald-600",
  Calm: "text-blue-600",
  Hopeful: "text-amber-600",
  Neutral: "text-muted-foreground",
  Anxious: "text-red-500",
  Sad: "text-indigo-500",
  Stressed: "text-orange-500",
  Tired: "text-purple-500",
};

function getMoodColor(mood: string) {
  return MOOD_COLORS[mood] ?? "text-muted-foreground";
}

function getScoreColor(score: string) {
  const pct = parseInt(score);
  if (pct >= 70) return "text-emerald-600";
  if (pct >= 50) return "text-amber-600";
  return "text-red-500";
}

function normalizeResponse<T>(res: any): T[] {
  const source = res?.data ?? res?.results ?? res?.result ?? res ?? [];
  return Array.isArray(source) ? source : (source?.results ?? []);
}

export default function CheckIns() {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [viewCheckIn, setViewCheckIn] =  useState<CheckInRow | null>(null);
  const [viewOpen, setViewOpen] = useState(false);

  const { data, isLoading, error } = useCheckins({
    page: currentPage,
    search: searchTerm || undefined,
  });
  const deleteMutation = useDeleteCheckin();

  const rows = data?.checkins ?? [];
  const metadata = data?.metadata ?? null;
  const totalItems = metadata?.total_items ?? rows.length;
  const totalPages = metadata?.total_pages ?? Math.max(1, Math.ceil(rows.length / ITEMS_PER_PAGE));
  const paginatedCheckIns = useMemo(() => rows.map(mapCheckIn), [rows]);

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Check-In</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">Review live user reflections and wellness scores.</p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error instanceof Error ? error.message : "Unable to load check-ins"}</div>}

      <div className="flex items-center justify-between gap-3">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search" value={searchTerm} onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }} className="h-9 pl-9 text-sm" />
        </div>

        <Button className="h-9 gap-1.5 text-sm font-medium" style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}>
          <CalendarDays className="h-4 w-4" />
          Today
        </Button>
      </div>

      {isLoading ? (
        <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground shadow-sm">Loading check-ins...</div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm min-h-[520px]">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent" style={{ backgroundColor: "rgba(209,61,61,0.06)" }}>
                {["Name", "Date", "Mood", "Score", "Action"].map((header) => (
                  <TableHead key={header} className="first:pl-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{header}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedCheckIns.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="py-12 text-center text-sm text-muted-foreground">No check-ins found.</TableCell>
                </TableRow>
              ) : (
                paginatedCheckIns.map((checkIn) => (
                  <TableRow key={checkIn.id} className="border-border transition-colors hover:bg-muted/40">
                    <TableCell className="py-3.5 pl-5"><span className="text-sm font-medium text-foreground">{checkIn.name}</span></TableCell>
                    <TableCell className="py-3.5"><span className="text-sm text-muted-foreground">{checkIn.date}</span></TableCell>
                    <TableCell className="py-3.5"><span className={`text-sm font-medium ${getMoodColor(checkIn.mood)}`}>{checkIn.mood}</span></TableCell>
                    <TableCell className="py-3.5"><span className={`text-sm font-medium ${getScoreColor(checkIn.score)}`}>{checkIn.score}</span></TableCell>
                    <TableCell className="py-3.5">
                      <DropdownMenu>
                        <DropdownMenuTrigger className="inline-flex h-8 items-center gap-1.5 rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/80 focus:outline-none">
                          Action
                          <ChevronDown className="h-3 w-3" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" className="w-44 rounded-lg">
                          <DropdownMenuItem className="cursor-pointer gap-2 text-sm" onClick={() => { setViewCheckIn(checkIn); setViewOpen(true); }}>
                            <Eye className="h-3.5 w-3.5 text-muted-foreground" /> View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem className="cursor-pointer gap-2 text-sm text-destructive focus:text-destructive" onClick={() => deleteMutation.mutate(checkIn.id)}>
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
      )}

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {totalItems === 0
            ? "No results"
            : `Showing ${(currentPage - 1) * ITEMS_PER_PAGE + 1}–${Math.min(currentPage * ITEMS_PER_PAGE, totalItems)} of ${totalItems}`}
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setCurrentPage((page) => Math.max(1, page - 1))} disabled={currentPage === 1} className="h-8 text-xs">Previous</Button>
          <Button variant="outline" size="sm" onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))} disabled={currentPage === totalPages || totalPages === 0} className="h-8 text-xs">Next</Button>
        </div>
      </div>
      <ViewCheckInDialog
      checkIn = {viewCheckIn}
      open = {viewOpen}
      onOpenChange = {setViewOpen}
      />
    </div>
  );
}