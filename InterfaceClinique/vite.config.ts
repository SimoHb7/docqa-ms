import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Split large vendor libraries into separate chunks
          'mui-core': ['@mui/material', '@mui/system'],
          'mui-icons': ['@mui/icons-material'],
          'mui-data': ['@mui/x-data-grid', '@mui/x-date-pickers'],
          'charts': ['chart.js', 'react-chartjs-2', 'recharts'],
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'auth': ['@auth0/auth0-react'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 3000,
    host: true,
    strictPort: true,
    proxy: {
      // API proxy configuration for development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => {
          // Keep the /api prefix and just ensure we're hitting the right endpoint
          const newPath = path.replace(/^\/api/, '/api/v1');
          console.log(`[Proxy] ${path} -> http://localhost:8000${newPath}`);
          return newPath;
        },
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('[Proxy Error]', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('[Proxy Request]', req.method, req.url, '->', proxyReq.getHeader('host'));
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('[Proxy Response]', req.method, req.url, proxyRes.statusCode);
          });
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable in production for faster load
    minify: 'esbuild', // Faster than terser
    target: 'esnext',
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            if (id.includes('@mui/material')) {
              return 'mui-material';
            }
            if (id.includes('@mui/icons-material')) {
              return 'mui-icons';
            }
            if (id.includes('@auth0')) {
              return 'auth-vendor';
            }
            if (id.includes('@tanstack/react-query')) {
              return 'query-vendor';
            }
            if (id.includes('chart.js')) {
              return 'chart-vendor';
            }
            return 'vendor';
          }
        },
      },
    },
  },
})