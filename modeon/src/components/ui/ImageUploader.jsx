// src/components/ui/ImageUploader.jsx
import { useRef, useState } from 'react';
import { Upload, ImagePlus } from 'lucide-react';

export default function ImageUploader({
  onFiles,
  multiple = false,
  maxFiles = 1,
  accept = 'image/*',
  label = 'Drag & drop or click to upload',
  sublabel,
  className = '',
}) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (fileList) => {
    const arr = Array.from(fileList).slice(0, maxFiles);
    if (arr.length) onFiles(arr);
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Upload images"
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files); }}
      className={`flex flex-col items-center justify-center gap-4 border-2 border-dashed rounded-2xl p-12 cursor-pointer transition-colors select-none
        ${dragging ? 'border-gold bg-gold/5' : 'border-divider hover:border-gold/60 hover:bg-surface/50'}
        ${className}`}
    >
      <div className="w-14 h-14 rounded-full bg-surface flex items-center justify-center text-taupe">
        <ImagePlus size={24} strokeWidth={1.5} />
      </div>
      <div className="text-center">
        <p className="text-sm font-semibold text-ink">{label}</p>
        {sublabel && <p className="text-xs text-muted mt-1">{sublabel}</p>}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        className="sr-only"
        aria-hidden="true"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
