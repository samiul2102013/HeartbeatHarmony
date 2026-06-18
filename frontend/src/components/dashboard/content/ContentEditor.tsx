"use client";

import { useMemo } from "react";
import "react-quill-new/dist/quill.snow.css";

const ReactQuill = dynamic(async () => (await import("react-quill-new")).default, { ssr: false });

import dynamic from "next/dynamic";

interface ContentEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

const TOOLBAR_OPTIONS = [
  [{ header: [1, 2, 3, false] }],
  ["bold", "italic", "underline", "strike"],
  [{ color: [] }, { background: [] }],
  [{ list: "ordered" }, { list: "bullet" }],
  ["blockquote", "code-block"],
  [{ align: [] }],
  ["link"],
  ["clean"],
];

export function ContentEditor({ value, onChange, placeholder }: ContentEditorProps) {
  const modules = useMemo(
    () => ({
      toolbar: TOOLBAR_OPTIONS,
    }),
    []
  );

  return (
    <div className="content-editor">
      <ReactQuill
        theme="snow"
        value={value}
        onChange={onChange}
        modules={modules}
        placeholder={placeholder}
      />
      <style jsx global>{`
        .content-editor .ql-editor {
          min-height: 400px;
          font-size: 15px;
          line-height: 1.7;
        }
        .content-editor .ql-toolbar {
          border-radius: 8px 8px 0 0;
          border-color: #e5e7eb;
        }
        .content-editor .ql-container {
          border-radius: 0 0 8px 8px;
          border-color: #e5e7eb;
        }
      `}</style>
    </div>
  );
}
