import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const configuredBase = process.env.VITE_BASE_PATH || '/';
const base = configuredBase.endsWith('/') ? configuredBase : `${configuredBase}/`;

export default defineConfig({
  // Locally this is `/`. The Pages workflow supplies its repository path, such
  // as `/pvz2-plant-atlas/`, so all generated asset links remain valid.
  base,
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(root, 'index.html'),
        print: resolve(root, 'PvZ2_Plants_Ancient_Egypt_A4_Print.html'),
        attributes: resolve(root, 'PvZ2_Plants_Ancient_Egypt_Attributes.html'),
      },
    },
  },
});
