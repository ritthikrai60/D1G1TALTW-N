import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import express from 'express';
import { createApiRouterAndWs } from './server/api.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function digitalTwinBackendPlugin() {
  return {
    name: 'digital-twin-backend',
    configureServer(viteServer) {
      const app = express();
      const { router, attachWebSocket } = createApiRouterAndWs();
      app.use('/api', router);
      const rackulaDistDir = path.resolve(__dirname, 'rackula', 'dist');
      app.use('/rackula', express.static(rackulaDistDir));
      app.use('/rackula', (req, res) => {
        res.sendFile(path.join(rackulaDistDir, 'index.html'));
      });
      viteServer.middlewares.use(app);
      if (viteServer.httpServer) {
        attachWebSocket(viteServer.httpServer);
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), digitalTwinBackendPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8085,
    host: true,
    watch: {
      ignored: ['**/data/**', '**/scripts/**', '**/tests/**'],
    },
  },
  preview: {
    port: 8085,
    host: true,
  },
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('three')) {
              return 'vendor-three';
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons';
            }
            if (id.includes('@radix-ui') || id.includes('class-variance-authority') || id.includes('clsx') || id.includes('tailwind-merge')) {
              return 'vendor-ui';
            }
          }
        },
      },
    },
  },
});
