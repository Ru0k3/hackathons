// src/components/wardrobe/UploadModal.jsx
import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, CheckCircle2, AlertCircle } from 'lucide-react';
import { useUploadWardrobeItems } from '@/hooks/useWardrobe';
import { addWardrobeItem } from '@/api/wardrobe';
import Modal from '@/components/ui/Modal';
import ProgressBar from '@/components/ui/ProgressBar';
import useUIStore from '@/stores/useUIStore';

const MAX_FILES = 20;
const MAX_SIZE_MB = 10;

export default function UploadModal({ open, onClose }) {
  const addToast = useUIStore((s) => s.addToast);
  useUploadWardrobeItems();
  const [files, setFiles] = useState([]);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const addFiles = (incoming) => {
    const valid = Array.from(incoming)
      .filter((f) => f.type.startsWith('image/') && f.size <= MAX_SIZE_MB * 1024 * 1024)
      .slice(0, MAX_FILES - files.length);

    setFiles((prev) => [
      ...prev,
      ...valid.map((f) => ({
        id: Math.random().toString(36).slice(2),
        file: f,
        name: f.name,
        preview: URL.createObjectURL(f),
        status: 'pending', // pending | uploading | done | error
        progress: 0,
      })),
    ]);
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  }, [files.length]);

  const removeFile = (id) => setFiles((prev) => prev.filter((f) => f.id !== id));

  const handleUpload = async () => {
    if (!files.length) return;

    for (const f of files) {
      setFiles((prev) =>
        prev.map((p) => p.id === f.id ? { ...p, status: 'uploading', progress: 30 } : p)
      );
      try {
        await addWardrobeItem(f.file, {});
        setFiles((prev) =>
          prev.map((p) => p.id === f.id ? { ...p, status: 'done', progress: 100 } : p)
        );
      } catch {
        setFiles((prev) =>
          prev.map((p) => p.id === f.id ? { ...p, status: 'error', progress: 0 } : p)
        );
      }
    }

    setTimeout(() => {
      setFiles([]);
      onClose();
    }, 1200);
  };

  return (
    <Modal open={open} onClose={onClose} title="Upload Items" size="lg">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors mb-6
          ${dragging ? 'border-gold bg-gold/5' : 'border-divider hover:border-gold/60 bg-surface'}`}
        aria-label="File drop zone"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      >
        <Upload size={32} className="mx-auto mb-3 text-muted" />
        <p className="font-bold text-ink mb-1">Drag &amp; drop photos here</p>
        <p className="text-sm text-muted">or click to browse - up to {MAX_FILES} items, {MAX_SIZE_MB} MB each</p>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          aria-label="Select files"
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="flex flex-col gap-3 mb-6 max-h-64 overflow-y-auto pr-1">
          <AnimatePresence>
            {files.map((f) => (
              <motion.div
                key={f.id}
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center gap-3 bg-surface rounded-xl p-3"
              >
                <img src={f.preview} alt={f.name} className="w-12 h-12 object-cover rounded-lg flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink truncate">{f.name}</p>
                  {f.status === 'uploading' && <ProgressBar value={f.progress} />}
                  {f.status === 'done' && (
                    <span className="flex items-center gap-1 text-ok text-xs font-medium">
                      <CheckCircle2 size={12} /> Uploaded
                    </span>
                  )}
                  {f.status === 'error' && (
                    <span className="flex items-center gap-1 text-danger text-xs font-medium">
                      <AlertCircle size={12} /> Failed
                    </span>
                  )}
                </div>
                {f.status === 'pending' && (
                  <button onClick={() => removeFile(f.id)} aria-label="Remove file" className="text-muted hover:text-danger flex-shrink-0">
                    <X size={16} />
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="btn-secondary">Cancel</button>
        <button
          onClick={handleUpload}
          disabled={!files.length}
          className="btn-gold"
          aria-label="Upload files"
        >
          <Upload size={15} />
          Upload {files.length > 0 ? `${files.length} item${files.length > 1 ? 's' : ''}` : 'Items'}
        </button>
      </div>
    </Modal>
  );
}
