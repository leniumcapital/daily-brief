/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
      },
      colors: {
        surface: "#f4f6f9",
        ink: "#0f172a",
        accent: "#4f46e5",
        finance: "#059669",
        markets: "#2563eb",
        startup: "#7c3aed",
        twitter: "#0ea5e9",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.04), 0 1px 2px -1px rgb(0 0 0 / 0.04)",
        elevated: "0 4px 24px -4px rgb(0 0 0 / 0.08)",
      },
    },
  },
  plugins: [],
};
