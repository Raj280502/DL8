import React, { useEffect, useState } from 'react';

import slideA from '../assets/6afbf7bf-fb8a-46e0-bc5d-fbf32f21b3b8.jpg';
import slideB from '../assets/bf506dcc-d43d-4891-8e66-f2533447061c.jpg';
import slideC from '../assets/pov_ medical life.jpg';

// Reuse provided assets to keep all slides local
const slideD = slideA;
const slideE = slideB;

const slides = [
  {
    image: slideA,
    title: 'Advanced AI Diagnostics',
    subtitle: 'Detecting critical conditions with unparalleled accuracy.',
  },
  {
    image: slideB,
    title: 'Pioneering Medical Technology',
    subtitle: 'Cutting-edge research for better patient outcomes.',
  },
  {
    image: slideC,
    title: 'Neuroanatomy Grounded',
    subtitle: 'Answers linked to your ingested textbook.',
  },
  {
    image: slideD,
    title: 'Clinician-Centric',
    subtitle: 'Designed with workflows for teams and trainees.',
  },
  {
    image: slideE,
    title: 'Secure & Fast',
    subtitle: 'HIPAA-aware patterns and sub-second retrievals.',
  },
];

const HeroSlider = ({ children }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
    }, 3200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative w-full min-h-[85vh] overflow-hidden rounded-3xl border border-border/60 shadow-xl">
      {slides.map((slide, index) => (
        <div
          key={index}
          className={`absolute inset-0 transition-opacity duration-1000 ${index === currentSlide ? 'opacity-100' : 'opacity-0'}`}
        >
          <img src={slide.image} alt={slide.title} className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-b from-black/55 via-black/45 to-black/70" />
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6 py-12 text-white">
            <p className="mb-3 inline-flex rounded-full bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-wide">
              {slide.title}
            </p>
            <p className="text-sm md:text-base text-white/80 max-w-2xl">{slide.subtitle}</p>
          </div>
        </div>
      ))}

      <div className="relative z-10 flex h-full items-center justify-center px-6 py-12">
        <div className="max-w-6xl w-full flex flex-col items-center text-center gap-6">
          {children}
        </div>
      </div>

      <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 gap-2">
        {slides.map((_, idx) => (
          <span
            key={idx}
            className={`h-2 w-2 rounded-full transition-all ${idx === currentSlide ? 'w-6 bg-white' : 'bg-white/50'}`}
            aria-label={`Slide ${idx + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default HeroSlider;