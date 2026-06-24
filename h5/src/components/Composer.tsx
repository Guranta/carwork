import { useRef, useState } from "react";
import { fileToCompressedDataUrl } from "../utils";

interface ComposerProps {
  disabled: boolean;
  onSend: (text: string, images: string[]) => void;
}

export default function Composer({ disabled, onSend }: ComposerProps) {
  const [text, setText] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);

  const pick = async (files: FileList | null) => {
    if (!files?.length) return;
    setBusy(true);
    try {
      const next: string[] = [];
      for (const file of Array.from(files).slice(0, 6)) {
        next.push(await fileToCompressedDataUrl(file));
      }
      setImages((prev) => [...prev, ...next].slice(0, 6));
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const grow = () => {
    const el = textRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 112)}px`;
  };

  const submit = () => {
    const trimmed = text.trim();
    if (disabled || busy || (!trimmed && images.length === 0)) return;
    onSend(trimmed, images);
    setText("");
    setImages([]);
    requestAnimationFrame(() => {
      if (textRef.current) textRef.current.style.height = "auto";
    });
  };

  return (
    <footer className="composer-shell">
      {images.length > 0 && (
        <div className="image-strip">
          {images.map((src, index) => (
            <div className="image-thumb" key={`${src.slice(0, 24)}_${index}`}>
              <img src={src} alt={`车损照片 ${index + 1}`} />
              <button onClick={() => setImages((prev) => prev.filter((_, i) => i !== index))}>×</button>
            </div>
          ))}
        </div>
      )}
      <div className="composer-row">
        <button className="camera-btn" disabled={disabled || busy} onClick={() => inputRef.current?.click()}>
          {busy ? "..." : "+"}
        </button>
        <textarea
          ref={textRef}
          rows={1}
          placeholder="问理赔、查保单，或上传车损照片..."
          value={text}
          onChange={(event) => { setText(event.target.value); grow(); }}
        />
        <button className="send-btn" disabled={disabled || busy || (!text.trim() && images.length === 0)} onClick={submit}>
          发送
        </button>
      </div>
      <input
        ref={inputRef}
        hidden
        multiple
        accept="image/*"
        type="file"
        onChange={(event) => void pick(event.target.files)}
      />
    </footer>
  );
}
