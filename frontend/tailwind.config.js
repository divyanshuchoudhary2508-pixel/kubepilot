/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // A VS Code / Linear / Raycast inspired neutral-dark palette.
        // Deliberately desaturated — accents carry the color, not the chrome.
        surface: {
          950: "#0a0b0d",
          900: "#0f1113",
          850: "#141619",
          800: "#1a1d21",
          700: "#24272c",
          600: "#32363c",
          border: "#2a2d32",
        },
        accent: {
          DEFAULT: "#5b8def",
          hover: "#4a7bd9",
          muted: "#5b8def1a",
        },
        danger: {
          DEFAULT: "#f2545b",
          muted: "#f2545b1a",
        },
        warning: {
          DEFAULT: "#e8a33d",
          muted: "#e8a33d1a",
        },
        success: {
          DEFAULT: "#3dd68c",
          muted: "#3dd68c1a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
      boxShadow: {
        subtle: "0 1px 2px rgba(0,0,0,0.24)",
        panel: "0 4px 16px rgba(0,0,0,0.32)",
      },
    },
  },
  plugins: [],
};
