import type { Config } from "tailwindcss";
const { fontFamily } = require("tailwindcss/defaultTheme");

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'egos-blue': '#003366', // Primary
        'egos-green': '#4CAF50', // Secondary
        'egos-pink': '#FFB6C1', // Accent
        'egos-lavender': '#E6E6FA', // Accent
        'egos-light-gray': '#F5F5F5', // Neutral
        'egos-mid-gray': '#EAEAEA', // Neutral
        // Add other shades if needed
      },
      fontFamily: {
        sans: ["var(--font-inter)", ...fontFamily.sans], // Body font
        serif: ["var(--font-playfair)", ...fontFamily.serif], // Heading font
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
