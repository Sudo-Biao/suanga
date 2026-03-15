import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Dev proxy — forwards API calls to the FastAPI backend
    proxy: {
      '/api': { target: 'http://localhost:8888', changeOrigin: true },
      '/health': { target: 'http://localhost:8888', changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom') || id.includes('react-router')) return 'vendor'
          if (id.includes('zustand')) return 'state'
        },
      },
    },
  },
})
