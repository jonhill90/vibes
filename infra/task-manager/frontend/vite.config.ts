import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Listen on all network interfaces
    port: 3000,
    strictPort: true,
    // Allow access from host.docker.internal (Docker Desktop internal DNS)
    allowedHosts: ["host.docker.internal", "localhost"],
    proxy: {
      "/api": {
        // Use host.docker.internal when VITE_API_URL is set (Docker environment)
        // Otherwise use localhost:8001 (local development)
        target: process.env.VITE_API_URL || "http://localhost:8001",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
    css: true,
    include: ["src/**/*.{test,spec}.{ts,tsx}", "tests/**/*.{test,spec}.{ts,tsx}"],
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      "**/.{idea,git,cache,output,temp}/**",
    ],
  },
});
