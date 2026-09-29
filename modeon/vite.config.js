import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },

  build: {
    // Warn at 1 MB instead of 500 kB — reasonable for a full app
    chunkSizeWarningLimit: 1000,

    rollupOptions: {
      output: {
        // Split vendor chunks so browsers can cache them separately
        manualChunks: {
          'vendor-react':    ['react', 'react-dom', 'react-router-dom'],
          'vendor-supabase': ['@supabase/supabase-js'],
          'vendor-axios':    ['axios'],
          'vendor-zustand':  ['zustand'],
          'vendor-posthog':  ['posthog-js'],
        },
      },
    },
  },

  server: {
    port: 3000,
    proxy: {
      // Proxy /api calls to the FastAPI backend during local dev
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
