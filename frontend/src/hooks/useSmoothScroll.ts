import { useEffect, useRef, useCallback } from "react";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Attaches Lenis smooth scrolling to a wrapper element and integrates
 * GSAP ScrollTrigger so both systems share the same scroll position.
 *
 * Returns a ref to attach to the scrollable `<main>` container.
 */
export function useSmoothScroll() {
  const wrapperRef = useRef<HTMLElement>(null);
  const lenisRef = useRef<Lenis | null>(null);

  // Scroll-to-top helper (call on route change)
  const scrollToTop = useCallback(() => {
    lenisRef.current?.scrollTo(0, { immediate: true });
  }, []);

  useEffect(() => {
    const wrapper = wrapperRef.current;
    if (!wrapper) return;

    const lenis = new Lenis({
      wrapper,
      content: wrapper.firstElementChild as HTMLElement,
      duration: 1.2,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      touchMultiplier: 1.5,
    });
    lenisRef.current = lenis;

    // Pipe Lenis scroll position into GSAP ScrollTrigger
    lenis.on("scroll", ScrollTrigger.update);

    // Tell ScrollTrigger to use this wrapper as its scroller for all triggers
    ScrollTrigger.defaults({ scroller: wrapper });

    // Sync Lenis into GSAP's ticker
    const tickerCb = (time: number) => {
      lenis.raf(time * 1000); // gsap ticker passes seconds, Lenis expects ms
    };
    gsap.ticker.add(tickerCb);
    gsap.ticker.lagSmoothing(0); // avoid frame skips in the smooth scroll

    return () => {
      gsap.ticker.remove(tickerCb);
      ScrollTrigger.getAll().forEach((t) => t.kill());
      lenis.destroy();
      lenisRef.current = null;
    };
  }, []);

  return { wrapperRef, scrollToTop };
}
