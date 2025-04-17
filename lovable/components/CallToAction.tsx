
import React from 'react';
import { Button } from "@/components/ui/button";

export const CallToAction = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-egos-plum to-egos-black text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-6">Join the Evolution. Build with Purpose.</h2>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          Be part of the movement for conscious, ethical, and beautiful technology.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Button size="lg" className="bg-egos-blue hover:bg-egos-blue/80 text-white px-8">
            Get Started with EGOS
          </Button>
          <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 px-8">
            Join Our Community
          </Button>
        </div>
      </div>
    </section>
  );
};
