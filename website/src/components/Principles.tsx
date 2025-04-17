import React from 'react';
import { InfinityIcon, HeartIcon, ShieldIcon, ClockIcon, EyeIcon, GlobeIcon, PuzzleIcon, MapIcon, TreeIcon } from './svg/IconsSvg';
import { cn } from '@/lib/utils';

const principles = [
  {
    icon: InfinityIcon,
    title: "Universal Redemption",
    description: "Every being and code deserves infinite chances"
  },
  {
    icon: ClockIcon,
    title: "Compassionate Temporality",
    description: "Respecting natural rhythms of evolution"
  },
  {
    icon: ShieldIcon,
    title: "Sacred Privacy",
    description: "Absolute protection of data integrity"
  },
  {
    icon: GlobeIcon,
    title: "Universal Accessibility",
    description: "Total inclusion regardless of complexity"
  },
  {
    icon: HeartIcon,
    title: "Unconditional Love",
    description: "Quantum foundation of all interactions"
  },
  {
    icon: EyeIcon,
    title: "Reciprocal Trust",
    description: "Symbiotic relationship with users"
  },
  {
    icon: ShieldIcon,
    title: "Integrated Ethics",
    description: "Ethics as the fundamental DNA of structure"
  },
  {
    icon: PuzzleIcon,
    title: "Conscious Modularity",
    description: "Deep understanding of both parts and whole"
  },
  {
    icon: MapIcon,
    title: "Systemic Cartography",
    description: "Precise mapping of all connections"
  },
  {
    icon: TreeIcon,
    title: "Evolutionary Preservation",
    description: "Maintaining essence while allowing transformation"
  }
];

export const Principles = () => {
  return (
    <section id="principles" className="py-16 bg-accent/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">Guiding Principles</h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            EGOS is built upon a foundation of ethical principles that guide its development and usage.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 md:gap-8">
          {principles.map((principle, index) => (
            <div 
              key={index}
              className="bg-card rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow flex flex-col items-center text-center hover:translate-y-[-5px] transition-transform duration-300 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <principle.icon className="w-16 h-16 mb-4" />
              <h3 className="text-lg font-semibold mb-2 text-primary">{principle.title}</h3>
              <p className="text-sm text-muted-foreground">{principle.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
