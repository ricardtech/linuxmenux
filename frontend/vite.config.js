import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8008',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8008',
        ws: true,
      },
    },
  },
  build: {
    outDir: path.resolve(import.meta.dirname, '../backend/static'),
    emptyOutDir: true,
    chunkSizeWarningLimit: 1000,
  },
});
