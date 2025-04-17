import React from 'react';
import { BrainIcon, MapIcon, ChatIcon, ShieldIcon, ClockIcon, GlobeIcon } from './svg/IconsSvg';
import { cn } from '@/lib/utils';

const subsystems = [
  {
    icon: ChatIcon,
    title: "Mycelium",
    description: "Semantic communication and messaging between all agents and modules"
  },
  {
    icon: BrainIcon,
    title: "Synapse",
    description: "Orchestration and workflow engine for distributed AI"
  },
  {
    icon: MapIcon,
    title: "KOIOS",
    description: "Living documentation, knowledge management, and system mapping"
  },
  {
    icon: ShieldIcon,
    title: "ETHIK",
    description: "Ethics engine for validation, transparency, and alignment"
  },
  {
    icon: ClockIcon,
    title: "Cronos",
    description: "Comprehensive logging, traceability, and evolutionary backup"
  },
  {
    icon: GlobeIcon,
    title: "Coruja",
    description: "Collaboration, review, and governance tools for human-AI teams"
  }
];

export const Subsystems = () => {
  return (
    <section id="subsystems" className="py-16 bg-background/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">Modular Subsystems</h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            EGOS consists of interconnected, modular subsystems that work together harmoniously.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {subsystems.map((subsystem, index) => (
            <div 
              key={index}
              className="bg-gradient-to-br from-card to-accent/20 rounded-lg shadow-md p-6 hover:shadow-lg transition-all border border-accent/30 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start">
                <subsystem.icon className="w-12 h-12 flex-shrink-0 mr-4" />
                <div>
                  <h3 className="text-xl font-semibold mb-2 text-primary">{subsystem.title}</h3>
                  <p className="text-muted-foreground">{subsystem.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
