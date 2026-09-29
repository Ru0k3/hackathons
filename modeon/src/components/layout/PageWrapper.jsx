// src/components/layout/PageWrapper.jsx
export default function PageWrapper({ children, className = '' }) {
  return (
    <div className={`max-w-6xl mx-auto px-10 py-12 ${className}`}>
      {children}
    </div>
  );
}
