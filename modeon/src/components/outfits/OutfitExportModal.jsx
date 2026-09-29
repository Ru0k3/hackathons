// src/components/outfits/OutfitExportModal.jsx
import { Download, Link2 } from 'lucide-react';
import { shareOutfit, downloadBlob } from '@/api/export';
import Modal from '@/components/ui/Modal';
import useUIStore from '@/stores/useUIStore';

export default function OutfitExportModal({ open, onClose, outfit }) {
  const addToast = useUIStore((s) => s.addToast);

  const handleDownload = async () => {
    if (!outfit?.id) return;
    try {
      const { supabase } = await import('@/lib/supabase');
      const { data } = await supabase.auth.getSession();
      const token = data?.session?.access_token;

      const response = await fetch(
        `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/outfits/${outfit.id}/export`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (!response.ok) {
        throw new Error('Download failed.');
      }

      const blob = await response.blob();
      downloadBlob(blob, `outfit-${outfit.id}.png`);
      addToast({ type: 'success', message: 'Download started.' });
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Download failed.' });
    }
  };

  const handleCopyLink = async () => {
    if (!outfit?.id) return;
    try {
      const { share_url } = await shareOutfit(outfit.id);
      await navigator.clipboard.writeText(share_url);
      addToast({ type: 'success', message: 'Share link copied!' });
    } catch (err) {
      addToast({ type: 'error', message: err?.message || 'Failed to create share link.' });
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Export Outfit">
      <p className="text-sm text-muted mb-6">
        Download your outfit as an image or copy a shareable link (valid 30 days).
      </p>
      <div className="flex flex-col gap-3">
        <button onClick={handleDownload} className="btn-primary w-full justify-center">
          <Download size={16} /> Download as Image
        </button>
        <button onClick={handleCopyLink} className="btn-secondary w-full justify-center">
          <Link2 size={16} /> Copy Share Link
        </button>
      </div>
    </Modal>
  );
}
