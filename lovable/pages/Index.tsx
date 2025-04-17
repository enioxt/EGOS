import React from 'react';
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { Principles } from '@/components/Principles';
import { Subsystems } from '@/components/Subsystems';
import { CallToAction } from '@/components/CallToAction';
import { Footer } from '@/components/Footer';

const Index = () => {
  return (
    <div className="min-h-screen bg-egos-off-white">
      <Header />
      <main>
        <Hero />
        <Principles />
        <Subsystems />
        <CallToAction />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
