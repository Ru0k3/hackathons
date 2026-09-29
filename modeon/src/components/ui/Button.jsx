// src/components/ui/Button.jsx
import { forwardRef } from 'react';

const VARIANTS = {
  primary:   'btn-primary',
  secondary: 'btn-secondary',
  gold:      'btn-gold',
  ghost:     'btn-ghost',
  danger:    'btn-danger',
};

const SIZES = {
  sm: 'px-4 py-2 text-2xs',
  md: '',   // default from class
  lg: 'px-9 py-4 text-xs',
};

const Button = forwardRef(function Button(
  { variant = 'primary', size = 'md', className = '', children, ...props },
  ref
) {
  const base    = VARIANTS[variant] ?? VARIANTS.primary;
  const sizeStr = SIZES[size] ?? '';
  return (
    <button ref={ref} className={`${base} ${sizeStr} ${className}`} {...props}>
      {children}
    </button>
  );
});

export default Button;
