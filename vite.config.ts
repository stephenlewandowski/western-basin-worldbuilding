import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

const page = (path: string) => fileURLToPath(new URL(path, import.meta.url));

export default defineConfig({
  base: '/western-basin-worldbuilding/',
  build: {
    rollupOptions: {
      input: {
        home: page('./index.html'),
        field: page('./atlas/field-to-lake/index.html'),
        crib: page('./atlas/toledo-crib/index.html'),
        farm: page('./atlas/farm-2075/index.html'),
        industry: page('./atlas/industrial-exchange/index.html'),
        methods: page('./methods/index.html'),
        roadmap: page('./roadmap/index.html'),
        game: page('./game/index.html'),
      },
    },
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
});
