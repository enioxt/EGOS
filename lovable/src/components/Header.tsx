
import React from 'react';
import { Button } from "@/components/ui/button"
import { Github, Menu, X } from "lucide-react";
import { useState } from "react";

export const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const toggleMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-sm bg-egos-off-white/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4 md:py-6">
          <div className="flex items-center">
            <span className="font-serif text-2xl font-medium text-egos-black">EGOS</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#principles" className="text-sm font-medium text-egos-black hover:text-egos-plum transition-colors">
              Principles
            </a>
            <a href="#subsystems" className="text-sm font-medium text-egos-black hover:text-egos-plum transition-colors">
              Subsystems
            </a>
            <a href="#generator" className="text-sm font-medium text-egos-black hover:text-egos-plum transition-colors">
              Prompt Generator
            </a>
            <a href="#roadmap" className="text-sm font-medium text-egos-black hover:text-egos-plum transition-colors">
              Roadmap
            </a>
            <a href="#community" className="text-sm font-medium text-egos-black hover:text-egos-plum transition-colors">
              Community
            </a>
            <Button variant="outline" className="ml-4 bg-transparent border-egos-plum text-egos-plum hover:bg-egos-plum hover:text-white transition-colors">
              <Github className="mr-2 h-4 w-4" />
              <span>GitHub</span>
            </Button>
          </nav>

          {/* Mobile menu button */}
          <button 
            className="md:hidden rounded-md p-2 inline-flex items-center justify-center text-egos-black hover:text-egos-plum"
            onClick={toggleMenu}
          >
            <span className="sr-only">Open menu</span>
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <a href="#principles" className="block px-3 py-2 rounded-md text-base font-medium text-egos-black hover:bg-egos-pastel-green">
              Principles
            </a>
            <a href="#subsystems" className="block px-3 py-2 rounded-md text-base font-medium text-egos-black hover:bg-egos-pastel-green">
              Subsystems
            </a>
            <a href="#generator" className="block px-3 py-2 rounded-md text-base font-medium text-egos-black hover:bg-egos-pastel-green">
              Prompt Generator
            </a>
            <a href="#roadmap" className="block px-3 py-2 rounded-md text-base font-medium text-egos-black hover:bg-egos-pastel-green">
              Roadmap
            </a>
            <a href="#community" className="block px-3 py-2 rounded-md text-base font-medium text-egos-black hover:bg-egos-pastel-green">
              Community
            </a>
            <div className="px-3 py-2">
              <Button className="w-full bg-egos-plum text-white hover:bg-opacity-80">
                <Github className="mr-2 h-4 w-4" />
                <span>GitHub</span>
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
