/** @type {import('tailwindcss').Config} */
export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        saint: {
          bg: "#f5f7f4",
          ink: "#17211b",
          muted: "#657267",
          line: "#d8dfd7",
          accent: "#1f6f64",
          strong: "#0e5149",
          soft: "#e8f1ee",
        },
      },
      boxShadow: {
        saint: "0 18px 50px rgba(23, 33, 27, 0.10)",
      },
    },
  },
  plugins: [],
};
