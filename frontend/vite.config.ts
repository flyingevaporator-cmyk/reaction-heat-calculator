import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import wasm from 'vite-plugin-wasm'
import topLevelAwait from 'vite-plugin-top-level-await'

export default defineConfig({
  plugins: [
    react(),
    wasm(),
    topLevelAwait(),
  ],
  define: {
    global: 'globalThis',
    'process.env': {},
    'process.platform': JSON.stringify(''),
    'process.version': JSON.stringify(''),
  },
  optimizeDeps: {
    exclude: ['ketcher-standalone'],
    include: [
      'lodash',
      'lodash/fp',
      '@babel/runtime/regenerator',
      '@babel/runtime/helpers/asyncToGenerator',
      '@babel/runtime/helpers/defineProperty',
      '@babel/runtime/helpers/objectSpread2',
      '@babel/runtime/helpers/slicedToArray',
      '@babel/runtime/helpers/toConsumableArray',
      '@babel/runtime/helpers/typeof',
      '@babel/runtime/helpers/extends',
      '@babel/runtime/helpers/inheritsLoose',
      '@babel/runtime/helpers/objectWithoutPropertiesLoose',
      'ketcher-react',
      'ketcher-core',
    ],
  },
  worker: {
    plugins: () => [
      wasm(),
      topLevelAwait(),
    ],
  },
  build: {
    target: 'esnext',
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
