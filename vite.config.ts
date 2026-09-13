import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "./" lets the built app run from any static host or local path
export default defineConfig({
  plugins: [react()],
  base: "./",
});
