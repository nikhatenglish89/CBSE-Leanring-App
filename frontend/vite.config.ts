import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Base path matches the GitHub Pages project-site URL (https://<user>.github.io/<repo>/).
// Override with VITE_BASE_PATH for other deploy targets (e.g. a custom domain uses "/").
export default defineConfig({
  base: process.env.VITE_BASE_PATH ?? "/CBSE-Leanring-App/",
  plugins: [react()],
  server: {
    port: 5173,
  },
});
