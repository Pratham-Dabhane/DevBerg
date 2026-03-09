import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Lenis from 'lenis'
import './index.css'
import App from './App'

/* ── Lenis smooth scroll ── */
const lenis = new Lenis({ duration: 1.1, easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
