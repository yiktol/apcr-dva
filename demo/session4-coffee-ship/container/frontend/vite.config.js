import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The SPA is baked into the container image and served same-origin by the
// Python app (CloudFront -> ALB -> ECS/Fargate). The API lives at the same
// origin under /order and /health, so no runtime config file is needed.
export default defineConfig({
  plugins: [react()],
  base: '/',
  build: { outDir: 'dist' },
});
