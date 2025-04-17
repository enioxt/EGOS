// src/app/en/page.tsx (Simplified for debugging)
"use client";

import { useTranslations } from 'next-intl';
import React from 'react'; // Ensure React is imported

// Commenting out complex component imports
// import { InfinityIcon, HeartIcon, ShieldIcon, ClockIcon, EyeIcon, GlobeIcon, PuzzleIcon, MapIcon, TreeIcon } from '@/components/svg/IconsSvg';
// import PrincipleCard from '@/components/content/PrincipleCard';
// import SubsystemCard from '@/components/content/SubsystemCard';
// import QuantumPromptGenerator from '@/components/features/QuantumPromptGenerator';
// import TechStackSection from '@/components/content/TechStackSection';
// import RoadmapSection from '@/components/content/RoadmapSection';

export default function Home() {
  const t = useTranslations('common'); // Keep the hook call

  return (
    <>
      <h1>{t('hero_title')}</h1> {/* Use a simple element with translation */}
      <p>Minimal page content for build test.</p>

      {/* All complex sections commented out below */}
      {/*
      <section className="hero-section bg-gradient-to-r from-primary to-primary-dark text-text-on-primary py-20 md:py-32 text-center relative overflow-hidden"> ... </section>
      <section id="vision" className="content-section py-12 md:py-16 bg-background-alt"> ... </section>
      <section id="principles" className="content-section py-12 md:py-16 bg-background"> ... </section>
      <section id="subsystems" className="content-section py-12 md:py-16 bg-background-alt"> ... </section>
      <section id="generator" className="content-section py-12 md:py-16 bg-background"> ... </section>
      <section id="tech-stack" className="content-section py-12 md:py-16 bg-background-alt"> ... </section>
      <section id="roadmap" className="content-section py-12 md:py-16 bg-background"> ... </section>
      */}
    </>
  );
}
