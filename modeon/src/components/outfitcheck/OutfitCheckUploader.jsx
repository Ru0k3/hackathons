// src/components/outfitcheck/OutfitCheckUploader.jsx
import { useRef }   from 'react';
import { Camera }   from 'lucide-react';
import Spinner      from '@/components/ui/Spinner';

export function OutfitCheckUploader({ onFile, uploading }) {
  const inputRef = useRef();
  return (
    <div
      onClick={() => !uploading && inputRef.current?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => { e.preventDefault(); onFile?.(e.dataTransfer.files[0]); }}
      className={`border-2 border-dashed rounded-2xl p-14 text-center transition-colors
        ${uploading ? 'opacity-60 cursor-wait' : 'cursor-pointer hover:border-gold/60 bg-surface border-divider'}`}
      role="button"
      tabIndex={0}
      aria-label="Upload outfit photo"
      onKeyDown={(e) => !uploading && e.key === 'Enter' && inputRef.current?.click()}
    >
      {uploading ? (
        <div className="flex flex-col items-center gap-3">
          <Spinner size="lg" />
          <p className="text-muted text-sm font-medium">Analysing your outfit…</p>
        </div>
      ) : (
        <>
          <Camera size={40} className="mx-auto mb-4 text-muted" />
          <p className="font-bold text-ink mb-1">Upload a photo of your outfit</p>
          <p className="text-sm text-muted">Get AI feedback on colour harmony, fit, and occasion match</p>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        aria-label="Select outfit photo"
        onChange={(e) => onFile?.(e.target.files?.[0])}
      />
    </div>
  );
}
