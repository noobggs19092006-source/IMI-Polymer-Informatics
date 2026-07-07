/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0F1419',
          secondary: '#1A1A2E',
        },
        accent: {
          primary: '#00D9FF',
          secondary: '#FF006E',
        },
        status: {
          success: '#4CAF50',
          error: '#FF5252',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#B0BEC5',
        },
        border: {
          DEFAULT: '#37474F',
        }
      },
      fontFamily: {
        mono: ['"Space Mono"', '"JetBrains Mono"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
