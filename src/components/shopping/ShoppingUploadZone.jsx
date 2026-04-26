// src/components/shopping/ShoppingUploadZone.jsx
import { useRef, useCallback } from 'react';
import { Upload }              from 'lucide-react';

export function ShoppingUploadZone({ onFile }) {
  const inputRef  = useRef();
  const [dragging, setDragging] = [false, () => {}]; // simplified

  const handleFile = (file) => {
    if (file && file.type.startsWith('image/')) onFile(file);
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
      className="border-2 border-dashed border-divider rounded-2xl p-12 text-center cursor-pointer hover:border-gold/60 transition-colors bg-surface"
      role="button"
      tabIndex={0}
      aria-label="Upload shopping item"
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
    >
      <Upload size={36} className="mx-auto mb-4 text-muted" />
      <p className="font-bold text-ink mb-1">Upload an item you're considering buying</p>
      <p className="text-sm text-muted">Drop an image here, or click to browse</p>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        aria-label="Select shopping item image"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
    </div>
  );
}
