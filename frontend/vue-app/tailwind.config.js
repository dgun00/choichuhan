/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}", // 👈 이 줄이 반드시 있어야 Tailwind가 Vue 파일 속 글자 크기와 배열 명령어를 읽어냅니다!
  ],
  theme: {
    extend: {
      colors: {
        cerulean: {
          50: '#f0f8ff', 100: '#e0f0fe', 300: '#7dd3fc',
          500: '#0ea5e9', 600: '#0284c7', 700: '#0f4c81',
          800: '#075985', 900: '#0c4a6e',
        }
      }
    },
  },
  plugins: [],
}

