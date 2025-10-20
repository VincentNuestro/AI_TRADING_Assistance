import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          500: "#38bdf8",
          600: "#0ea5e9"
        }
      }
    }
  },
  plugins: []
};

export default config;
