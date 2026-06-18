import path from "path"
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const env = loadEnv(process.cwd(), '')
const additionalAllowedHosts = env.VITE_ALLOWED_HOST

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      additionalAllowedHosts,
    ],
  },
})
