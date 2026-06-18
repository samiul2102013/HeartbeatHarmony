"use client";

import { useRef, useCallback } from "react";

interface ContentEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function ContentEditor({ value, onChange, placeholder }: ContentEditorProps) {
  const ref = useRef<HTMLDivElement>(null);

  const onInput = useCallback(() => {
    if (ref.current) {
      onChange(ref.current.innerHTML);
    }
  }, [onChange]);

  return (
    <div className="border border-input rounded-lg overflow-hidden">
      <Toolbar editorRef={ref} />
      <div
        ref={ref}
        contentEditable
        suppressContentEditableWarning
        className="min-h-[400px] p-4 text-sm focus:outline-none leading-relaxed"
        style={{ lineHeight: "1.7" }}
        onInput={onInput}
        onBlur={onInput}
        dangerouslySetInnerHTML={{ __html: value }}
        data-placeholder={placeholder}
      />
    </div>
  );
}

function Toolbar({ editorRef }: { editorRef: React.RefObject<HTMLDivElement | null> }) {
  const exec = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  const btnClass = "px-2 py-1 text-sm rounded hover:bg-muted border border-transparent hover:border-border transition-colors";

  return (
    <div className="flex flex-wrap items-center gap-0.5 p-2 border-b border-input bg-muted/30">
      <select
        className="h-7 text-xs rounded border border-input bg-background px-1"
        onChange={(e) => { exec("formatBlock", e.target.value); e.target.value = ""; }}
        defaultValue=""
      >
        <option value="" disabled>Heading</option>
        <option value="h1">H1</option>
        <option value="h2">H2</option>
        <option value="h3">H3</option>
        <option value="p">Paragraph</option>
      </select>

      <span className="w-px h-5 bg-border mx-1" />

      <button type="button" className={btnClass} onClick={() => exec("bold")} title="Bold"><strong>B</strong></button>
      <button type="button" className={btnClass} onClick={() => exec("italic")} title="Italic"><em>I</em></button>
      <button type="button" className={btnClass} onClick={() => exec("underline")} title="Underline"><u>U</u></button>
      <button type="button" className={btnClass} onClick={() => exec("strikeThrough")} title="Strikethrough"><s>S</s></button>

      <span className="w-px h-5 bg-border mx-1" />

      <button type="button" className={btnClass} onClick={() => exec("insertOrderedList")} title="Ordered List">OL</button>
      <button type="button" className={btnClass} onClick={() => exec("insertUnorderedList")} title="Bullet List">UL</button>

      <span className="w-px h-5 bg-border mx-1" />

      <input
        type="color"
        className="w-6 h-6 p-0 border-0 cursor-pointer"
        onChange={(e) => exec("foreColor", e.target.value)}
        title="Text Color"
      />
      <input
        type="color"
        className="w-6 h-6 p-0 border-0 cursor-pointer"
        onChange={(e) => exec("hiliteColor", e.target.value)}
        title="Highlight Color"
      />

      <button type="button" className={btnClass} onClick={() => exec("removeFormat")} title="Remove Formatting">Clear</button>
    </div>
  );
}
