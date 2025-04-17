
import React from 'react';
import { Button } from "@/components/ui/button";
import { NetworkSvg } from './svg/NetworkSvg';
import { CodeBlocksSvg } from './svg/CodeBlocksSvg';
import { WaveSvg } from './svg/WaveSvg';

export const Hero = () => {
  return (
    <div className="relative pt-20 pb-16 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-egos-lavender/30 to-transparent"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-egos-black">
                <span className="font-serif italic">Evolving.</span>{" "}
                <span className="block md:inline text-egos-plum">Ethical.</span>{" "}
                <span className="block md:inline">Generative.</span>
              </h1>
              <p className="mt-6 text-xl text-gray-600 max-w-3xl">
                EGOS empowers you to build conscious AI, blending technology, ethics, and art.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Button className="bg-gradient-to-r from-egos-plum to-egos-blue text-white px-8 py-6 text-lg hover:opacity-90 transition-opacity">
                Explore EGOS
              </Button>
              <Button variant="outline" className="border-egos-plum text-egos-plum hover:bg-egos-plum/10 px-8 py-6 text-lg">
                View Documentation
              </Button>
            </div>
            
            <div className="flex gap-6 items-center text-sm text-gray-500">
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-egos-pink mr-2"></div>
                <span>Open-source</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-egos-lime mr-2"></div>
                <span>Universal</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-egos-blue mr-2"></div>
                <span>Beautiful</span>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="relative flex justify-center">
              <div className="w-full h-[400px] bg-gradient-to-br from-egos-lavender/30 to-egos-pastel-green/30 rounded-2xl shadow-lg overflow-hidden relative">
                <div className="absolute inset-0 flex">
                  <div className="w-1/2 border-r border-white/10">
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
