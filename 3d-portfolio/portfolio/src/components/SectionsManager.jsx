// SectionsManager.jsx

import React from 'react';
import ParticleText from './ParticleText';
import Hero from './Hero';
import About from './About';
import Experience from './Experience';
import Tech from './Tech';
import Works from './Works';
import Feedbacks from './Feedbacks';
import Contact from './Contact';

const SectionsManager = () => {
  const sections = [
    {
      text: "HI,\nI'M JOAQUIN",
      position: { x: 0, y: 0 },
      size: 16,
      startScroll: 0,
    },
    {
      text: 'ABOUT',
      position: { x: -50, y: 50 }, // Adjust based on your layout
      size: 8,
      startScroll: 20,
    },
    {
      text: 'EXPERIENCE',
      position: { x: -50, y: 50 },
      size: 8,
      startScroll: 50,
    },
    // ... (other sections)
  ];

  return (
    <div>
      <ParticleText sections={sections} />
      <About />
      <Experience />
      <Tech />
      <Works />
      <Feedbacks />
      <Contact />
    </div>
  );
};

export default SectionsManager;