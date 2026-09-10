import { createServer, build } from 'vite';
import vue from '@vitejs/plugin-vue';
import react from '@vitejs/plugin-react';
import tailwind from '@tailwindcss/vite';
import path from 'node:path';
const root = process.env.OMAGYM_PROJECT;
const modules = path.resolve(import.meta.dirname, '../../node_modules');
const config = {
  configFile: false, root, base: process.argv.includes('--build') ? './' : '/', cacheDir: path.join(root, '.vite'),
  plugins: [vue(), react(), ...(process.env.OMAGYM_TRACK === 'tailwind' ? [tailwind()] : [])],
  resolve: { alias: {
    react: path.join(modules, 'react'), 'react-dom': path.join(modules, 'react-dom'),
    vue: path.join(modules, 'vue/dist/vue.esm-bundler.js'), tailwindcss: path.join(modules, 'tailwindcss'),
  } },
  server: { host: '127.0.0.1', port: Number(process.env.OMAGYM_PORT || 4399), strictPort: true, fs: { strict: true, allow: [root, modules] } },
  build: { outDir: path.join(root, '.preview'), emptyOutDir: true },
};
if (process.argv.includes('--build')) await build(config);
else { const server = await createServer(config); await server.listen(); }
