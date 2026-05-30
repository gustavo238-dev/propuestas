import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        harbor: "#075985",
        signal: "#0F766E",
        cargo: "#B45309",
        line: "#D8DEE8",
        surface: "#F6F8FB"
      },
      boxShadow: {
        panel: "0 12px 28px rgba(15, 23, 42, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
