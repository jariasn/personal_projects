// src/hooks/useParallax.js
import { useTransform, useScroll } from 'framer-motion';

export function useParallax(ref, distance) {
  const { scrollYProgress } = useScroll({ target: ref });
  return useTransform(scrollYProgress, [0, 1], [-distance, distance]);
}