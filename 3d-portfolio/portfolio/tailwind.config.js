/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}"],
  mode: "jit",
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',      // Uses CSS variable
        secondary: 'var(--color-secondary)',  // Uses CSS variable
        tertiary: 'var(--color-tertiary)',    // Uses CSS variable
        'black-100': 'var(--color-black-100)',// Uses CSS variable
        'black-200': 'var(--color-black-200)',
        'white-100': 'var(--color-white-100)',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(270deg, var(--color-primary), var(--color-gradient))', // Dark gradient
        'grid-overlay': `linear-gradient(to right, var(--color-grid) 1px, transparent 1px),
                         linear-gradient(to bottom, var(--color-grid) 1px, transparent 1px)`, 
      },
      backgroundSize: {
        'grid-overlay': '200px 200px', 
      },

      boxShadow: {
        card: '0px 35px 120px -15px var(--color-shadow-card)', 
        glow: '0 0 50px 10px rgba(0, 93, 233, 0.5)'
      },
      screens: {
        xs: "450px",
      },
      keyframes: {
        circle: {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '50%': { transform: 'translate(20px, 20px)' },
        },
        'circle-reverse': {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '50%': { transform: 'translate(-20px, -20px)' },
        },
      },
      animation: {
        circle: 'circle 4s infinite ease-in-out',
        'circle-reverse': 'circle-reverse 4s infinite ease-in-out',
      },
    },
  },
  plugins: [],
};