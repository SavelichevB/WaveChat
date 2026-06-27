import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://localhost:3333',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://localhost:3333',
        changeOrigin: true,
      },
      '/message': {
        target: 'http://localhost:3333',
        changeOrigin: true,
      },
      '/users': {
        target: 'http://localhost:3333',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:3333',
        ws: true,
      },
    },
  },
})
