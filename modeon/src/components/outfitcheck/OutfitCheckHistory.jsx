// src/components/outfitcheck/OutfitCheckHistory.jsx
import { Star, Calendar } from 'lucide-react';
import EmptyState         from '@/components/ui/EmptyState';
import { Camera }         from 'lucide-react';

export function OutfitCheckHistory({ checks }) {
  if (!checks.length) {
    return (
      <EmptyState
        icon={Camera}
        title="No outfit checks yet"
        description="Upload a photo of your outfit above to get your first AI analysis."
      />
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {checks.map((check) => (
        <div key={check.check_id} className="card p-4 flex gap-4 items-start">
          {check.image_sas_url && (
            <div className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 bg-surface">
              <img src={check.image_sas_url} alt="Outfit check" className="w-full h-full object-cover" />
            </div>
          )}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <div className="flex gap-0.5">
                {Array.from({ length: 10 }).map((_, i) => (
                  <Star
                    key={i}
                    size={12}
                    className={i < Math.round(check.overall_score) ? 'text-gold' : 'text-divider'}
                    fill={i < Math.round(check.overall_score) ? 'currentColor' : 'none'}
                  />
                ))}
              </div>
              <span className="text-2xs font-bold text-gold">{check.overall_score}/10</span>
            </div>
            <p className="text-sm text-taupe italic line-clamp-2">{check.summary}</p>
            {check.checked_at && (
              <span className="flex items-center gap-1 text-2xs text-muted mt-2">
                <Calendar size={10} /> {check.checked_at}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
