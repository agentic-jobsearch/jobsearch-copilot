import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

VITE_API_BASE_URL="http://127.0.0.1:8000"


// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})
