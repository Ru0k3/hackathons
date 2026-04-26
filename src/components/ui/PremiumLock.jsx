// src/components/ui/PremiumLock.jsx
// All features are unlocked — this component is a transparent passthrough.
// The locked prop and featureName are kept for API compatibility but have no effect.

export default function PremiumLock({ children }) {
  return <>{children}</>;
}
