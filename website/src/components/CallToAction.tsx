import React from 'react';
import { Button } from '@/components/ui/button';

export const CallToAction = () => {
  return (
    <section className="py-12 md:py-20 bg-gradient-to-br from-background to-muted text-foreground">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold mb-4 md:mb-6">Join the Evolution. Build with Purpose.</h2>
        <p className="text-base md:text-xl text-muted-foreground mb-6 md:mb-8 max-w-2xl mx-auto">
          Be part of the movement for conscious, ethical, and beautiful technology.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-3 md:gap-4">
          <a href="https://github.com/enioxt/EGOS" target="_blank" rel="noopener noreferrer">
            <Button size="lg" className="px-6 md:px-8 w-full sm:w-auto">
              Get Started with EGOS
            </Button>
          </a>
          <a href="https://github.com/enioxt/EGOS/discussions" target="_blank" rel="noopener noreferrer">
            <Button size="lg" variant="outline" className="px-6 md:px-8 w-full sm:w-auto">
              Join Our Community
            </Button>
          </a>
        </div>
      </div>
    </section>
  );
};
