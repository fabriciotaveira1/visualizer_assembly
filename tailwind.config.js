/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#2563eb",
          600: "#1d4ed8",
          700: "#1e40af",
        },
        slate: {
          950: "#020617",
        },
      },
      boxShadow: {
        panel: "0 24px 60px rgba(15, 23, 42, 0.18)",
      },
      backgroundImage: {
        "hero-grid":
          "radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 30%), radial-gradient(circle at bottom right, rgba(14,165,233,0.18), transparent 28%)",
      },
    },
  },
  plugins: [],
};
