import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/classes': 'http://localhost:8000',
      '/students': 'http://localhost:8000',
      '/attendance': 'http://localhost:8000',
      '/reports': 'http://localhost:8000',
    }
  }
})
