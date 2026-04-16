/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        sand: "#f5efe6",
        flame: "#e4572e",
        tide: "#0f766e"
      },
      boxShadow: {
        card: "0 10px 30px rgba(0, 0, 0, 0.1)"
      }
    }
  },
  plugins: []
};
