/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        background: '#0a0c10', // Deep slate/charcoal
        surface: '#11141a', // Slightly lighter for cards
        border: 'rgba(255, 255, 255, 0.08)', // Subtle 1px stroke
        ai: {
          blue: '#4f8bff', // Sophisticated muted electric blue
          emerald: '#34d399', // Emerald
        }
      },
      letterSpacing: {
        tight: '-0.015em',
        tighter: '-0.025em',
      },
    },
  },
  plugins: [],
}
