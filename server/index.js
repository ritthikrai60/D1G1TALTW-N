import http from 'node:http';
import path from 'node:path';
import fs from 'node:fs';
import express from 'express';
import { createApiRouterAndWs } from './api.js';

const PORT = Number(process.env.PORT || 8085);
const app = express();
const server = http.createServer(app);

const { router, attachWebSocket } = createApiRouterAndWs();
app.use('/api', router);
attachWebSocket(server);

// Serve Rackula 19-inch Rack Elevation Designer Sub-App
const rackulaDistDir = path.resolve(process.cwd(), 'rackula', 'dist');
if (fs.existsSync(rackulaDistDir)) {
  app.use('/rackula', express.static(rackulaDistDir));
  app.use('/rackula', (req, res) => {
    res.sendFile(path.join(rackulaDistDir, 'index.html'));
  });
}

const distDir = path.resolve(process.cwd(), 'dist');
if (fs.existsSync(distDir)) {
  app.use(express.static(distDir));
  // SPA fallback for `/` and `/admin`
  app.get('*', (req, res) => {
    res.sendFile(path.join(distDir, 'index.html'));
  });
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`=========================================================`);
  console.log(` LUDUS Digital Twin & Network Command Server`);
  console.log(` Viewer Mode : http://localhost:${PORT}/`);
  console.log(` Admin Portal: http://localhost:${PORT}/admin`);
  console.log(`=========================================================`);
});

