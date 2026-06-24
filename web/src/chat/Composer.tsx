import { useRef, useState } from "react";
import { fileToCompressedDataUrl } from "./utils";

export default function Composer({
  onSend,
  disabled,
}: {
  onSend: (text: string, images: string[]) => void;
  disabled: boolean;
}) {
  const [text, setText] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);

  const autoGrow = () => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 110) + "px";
  };

  const onPick = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setBusy(true);
    try {
      const uris: string[] = [];
      for (const f of Array.from(files).slice(0, 6)) {
        uris.push(await fileToCompressedDataUrl(f));
      }
      setImages((prev) => [...prev, ...uris].slice(0, 6));
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const submit = () => {
    const t = text.trim();
    if ((!t && images.length === 0) || disabled) return;
    onSend(t, images);
    setText("");
    setImages([]);
    requestAnimationFrame(() => {
      if (taRef.current) taRef.current.style.height = "auto";
    });
  };

  return (
    <div className="chat-composer">
      {images.length > 0 && (
        <div className="preview-row">
          {images.map((src, i) => (
            <div className="thumb" key={i}>
              <img src={src} alt={`预览${i + 1}`} />
              <button
                className="rm"
                onClick={() => setImages((prev) => prev.filter((_, idx) => idx !== i))}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="composer-row">
        <button
          className="add-btn"
          onClick={() => fileRef.current?.click()}
          disabled={busy || disabled}
          aria-label="上传图片"
        >
          {busy ? "…" : "+"}
        </button>
        <textarea
          ref={taRef}
          rows={1}
          placeholder="输入问题，或点 + 拍照上传车损…"
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            autoGrow();
          }}
          onKeyDown={(e) => {
            // 桌面端 Ctrl/Cmd+Enter 发送；移动端回车换行
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button
          className="send-btn"
          onClick={submit}
          disabled={disabled || busy || (!text.trim() && images.length === 0)}
          aria-label="发送"
        >
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M3.4 20.4 21 12 3.4 3.6 3 10l12 2-12 2 .4 6.4Z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        multiple
        style={{ display: "none" }}
        onChange={(e) => onPick(e.target.files)}
      />
    </div>
  );
}
