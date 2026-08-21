import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7ff",
          100: "#d9edff",
          200: "#bce0ff",
          300: "#8ecdff",
          400: "#59b1ff",
          500: "#2f8fff",
          600: "#1a6ff5",
          700: "#1558e0",
          800: "#1846b5",
          900: "#193e8d",
        },
        accent: {
          50: "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
          300: "#fdba74",
          400: "#fb923c",
          500: "#f97316",
          600: "#ea580c",
          700: "#c2410c",
        },
        violet: {
          50: "#f5f3ff",
          100: "#ede9fe",
          500: "#8b5cf6",
          600: "#7c3aed",
          700: "#6d28d9",
        },
        rose: {
          50: "#fff1f4",
          100: "#ffe4e9",
          500: "#fb7185",
          600: "#e11d48",
          700: "#be123c",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Lexend", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(15, 23, 42, 0.04), 0 12px 28px -8px rgba(15, 23, 42, 0.12)",
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 12px -4px rgba(15, 23, 42, 0.08)",
        lift: "0 1px 2px rgba(15, 23, 42, 0.04), 0 20px 40px -12px rgba(21, 88, 224, 0.22)",
      },
      backgroundImage: {
        "hero-grid":
          "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.14) 1px, transparent 0)",
        "dot-grid":
          "radial-gradient(circle at 1px 1px, rgba(15,23,42,0.08) 1px, transparent 0)",
      },
    },
  },
  plugins: [],
} satisfies Config;
