import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://gateway:8080',
        changeOrigin: true,
      },
    },
    host: '0.0.0.0',
    port: 3000,
  },
})
