import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // when running "npm run dev", send /api calls to the backend on port 8000
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
