import React from 'react';
import { Button } from "@/components/ui/button";
import { NetworkSvg } from '@/components/svg/NetworkSvg';
import { CodeBlocksSvg } from '@/components/svg/CodeBlocksSvg';
import { WaveSvg } from '@/components/svg/WaveSvg';
import { cn } from '@/lib/utils';

export const Hero = () => {
  return (
    <div className="relative pt-20 pb-16 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-accent/30 to-transparent"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 md:pt-16 pb-16 md:pb-24 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12 items-center">
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
                <span className="font-serif italic">Evolving.</span>{" "}
                <span className="block md:inline text-primary">Ethical.</span>{" "}
                <span className="block md:inline">Generative.</span>
              </h1>
              <p className="mt-6 text-xl text-muted-foreground max-w-3xl">
                EGOS empowers you to build conscious AI, blending technology, ethics, and art.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3 md:gap-4">
              <a href="/#principles">
                <Button className="bg-gradient-to-r from-primary to-primary text-primary-foreground px-6 md:px-8 py-5 md:py-6 text-base md:text-lg hover:opacity-90 transition-opacity w-full sm:w-auto">
                  Explore EGOS
                </Button>
              </a>
              <a href="https://github.com/enioxt/EGOS" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="border-primary text-primary hover:bg-primary/10 px-6 md:px-8 py-5 md:py-6 text-base md:text-lg w-full sm:w-auto">
                  View on GitHub
                </Button>
              </a>
            </div>
            
            <div className="flex gap-6 items-center text-sm text-muted-foreground">
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-accent mr-2"></div>
                <span>Open-source</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-secondary mr-2"></div>
                <span>Universal</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-primary mr-2"></div>
                <span>Beautiful</span>
              </div>
            </div>
          </div>
          
          <div className="relative mt-6 lg:mt-0">
            <div className="relative flex justify-center">
              <div className="w-full h-[300px] md:h-[400px] bg-gradient-to-br from-accent/30 to-accent/30 rounded-lg md:rounded-2xl shadow-lg overflow-hidden relative">
                <div className="absolute inset-0 flex">
                  <div className="w-1/2 border-r border-border/10">
                    <NetworkSvg className="w-full h-full" />
                  </div>
                  <div className="w-1/2">
                    <CodeBlocksSvg className="w-full h-full" />
                  </div>
                </div>
              </div>
              <div className="absolute -bottom-6 left-0 right-0 h-20 pointer-events-none">
                <WaveSvg className="w-full h-full" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
