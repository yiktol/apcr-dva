import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The app reads runtime config from /config.js (generated at deploy time and
// uploaded to the S3 bucket), so the same build works against any stack.
export default defineConfig({
  plugins: [react()],
  build: { outDir: 'dist' },
});
