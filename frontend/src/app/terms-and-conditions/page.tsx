"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function TermsAndConditionsPage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/terms-and-conditions/`, { cache: "no-store" })
      .then((r) => r.json())
      .then((res) => {
        if (res?.data) {
          setTitle(res.data.title);
          setContent(res.data.content);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-3xl mx-auto px-4 py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">{title}</h1>
        <div
          className="prose prose-sm max-w-none text-gray-700"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      </div>
    </div>
  );
}
