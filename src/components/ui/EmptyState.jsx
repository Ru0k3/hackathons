// src/components/ui/EmptyState.jsx
export default function EmptyState({ icon: Icon, heading, title, body, description, action }) {
  const h = heading || title;
  const b = body || description;
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center gap-4">
      {Icon && (
        <div className="w-16 h-16 rounded-full bg-surface flex items-center justify-center text-muted">
          <Icon size={28} strokeWidth={1.5} />
        </div>
      )}
      {h && <h3 className="font-display text-2xl text-ink">{h}</h3>}
      {b && <p className="text-muted text-sm max-w-xs leading-relaxed">{b}</p>}
      {action}
    </div>
  );
}
