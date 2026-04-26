// src/pages/MyOutfitsPage.jsx
import { useState } from 'react';
import PageWrapper from '@/components/layout/PageWrapper';
import OutfitGallery from '@/components/outfits/OutfitGallery';
import OutfitExportModal from '@/components/outfits/OutfitExportModal';
import { useSavedOutfits, useDeleteOutfit } from '@/hooks/useOutfits';

export default function MyOutfitsPage() {
  const { data, isLoading } = useSavedOutfits();
  const outfits = data?.outfits ?? [];
  const { mutate: deleteOutfit } = useDeleteOutfit();
  const [exportTarget, setExportTarget] = useState(null);

  return (
    <PageWrapper>
      <header className="mb-10">
        <h1 className="font-display text-5xl mb-1">My Outfits</h1>
        <p className="text-sm text-muted italic">{outfits.length} saved ensembles</p>
      </header>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="w-10 h-10 border-2 border-gold border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <OutfitGallery
          outfits={outfits}
          onDelete={(id) => deleteOutfit(id)}
          onShare={(outfit) => setExportTarget(outfit)}
        />
      )}

      <OutfitExportModal
        open={!!exportTarget}
        outfit={exportTarget}
        onClose={() => setExportTarget(null)}
      />
    </PageWrapper>
  );
}
