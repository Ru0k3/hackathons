// src/components/ui/Spinner.jsx
const SIZES = { sm: 'w-4 h-4', md: 'w-7 h-7', lg: 'w-12 h-12' };

export default function Spinner({ size = 'md', className = '' }) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={`${SIZES[size] ?? SIZES.md} rounded-full border-2 border-divider border-t-gold animate-spin ${className}`}
    />
  );
}
