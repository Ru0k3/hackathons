/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#fdf8f3',
          100: '#f7f0e6',
          200: '#ede8df',
          300: '#d9d3c8',
          400: '#c8a97e',
          500: '#b8945e',
          600: '#a07840',
          700: '#8a6432',
          800: '#6b4e27',
          900: '#4a3519',
        },
        // Alias tokens for Modeon design system
        canvas:  '#EDE8DF',
        surface: '#E6E1D8',
        card:    '#F7F3EE',
        ink:     '#1C1916',
        gold:    '#C8A97E',
        taupe:   '#8C7B6B',
        muted:   '#9E9189',
        divider: '#D9D3C8',
        ok:      '#7BAE8E',
        danger:  '#C47B72',
      },
      fontFamily: {
        sans:    ['DM Sans', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '1rem' }],
      },
      borderRadius: {
        card: '1.5rem',
        chip: '9999px',
      },
      boxShadow: {
        card:   '0 4px 20px rgba(0,0,0,0.05)',
        float:  '0 8px 32px rgba(0,0,0,0.10)',
        gold:   '0 8px 20px rgba(200,169,126,0.28)',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'fade-up':   'fadeUp 0.4s ease forwards',
      },
      keyframes: {
        fadeUp: {
          '0%':   { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
