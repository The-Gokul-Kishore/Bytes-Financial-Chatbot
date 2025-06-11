import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5100,
    proxy: {
      '/upload': 'http://localhost:5000'
    }
  }
})
