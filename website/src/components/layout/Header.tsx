'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Globe, Menu, X, ChevronDown } from 'lucide-react';

// Simplified version that doesn't rely on translations initially
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLangDropdownOpen, setIsLangDropdownOpen] = useState(false);
  const pathname = usePathname();
  const locale = 'en'; // Default locale for now

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    if (isLangDropdownOpen) setIsLangDropdownOpen(false);
  };

  const toggleLangDropdown = () => {
    setIsLangDropdownOpen(!isLangDropdownOpen);
  };

  return (
    <header className="fixed top-0 left-0 w-full bg-background/80 backdrop-blur-sm shadow-sm z-50 p-4">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo */}
        <div>
          <Link href="/" className="text-xl font-serif font-bold text-foreground">
            EGOS
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          <a href="/#principles" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Principles
          </a>
          <a href="/#subsystems" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Subsystems
          </a>
          <a href="/#roadmap" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Roadmap
          </a>
          
          {/* Language Switcher - Simplified */}
          <button 
            onClick={toggleLangDropdown}
            className="flex items-center text-muted-foreground hover:text-foreground" 
          >
            <Globe className="mr-1 h-4 w-4" />
            <span className="uppercase">EN</span> 
            <ChevronDown className={`ml-1 h-3 w-3 transition-transform ${isLangDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {isLangDropdownOpen && (
            <div className="absolute mt-16 bg-background border border-border rounded-md shadow-md p-2">
              <Link href={pathname} locale="en" className="block px-4 py-2 text-sm hover:bg-muted rounded-sm">English</Link>
              <Link href={pathname} locale="pt" className="block px-4 py-2 text-sm hover:bg-muted rounded-sm">Português</Link>
            </div>
          )}
        </nav>

        {/* Mobile menu button */}
        <button 
          className="md:hidden p-2 text-muted-foreground hover:text-foreground" 
          onClick={toggleMenu}
        >
          {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <nav className="md:hidden bg-background py-4 border-t border-border mt-4">
          <div className="container mx-auto flex flex-col space-y-3">
            <a href="/#principles" onClick={toggleMenu} className="px-4 py-2 text-muted-foreground hover:text-foreground">
              Principles
            </a>
            <a href="/#subsystems" onClick={toggleMenu} className="px-4 py-2 text-muted-foreground hover:text-foreground">
              Subsystems
            </a>
            <a href="/#roadmap" onClick={toggleMenu} className="px-4 py-2 text-muted-foreground hover:text-foreground">
              Roadmap
            </a>
            <div className="px-4 py-2 border-t border-border mt-2 pt-2 flex space-x-4">
              <Link href={pathname} locale="en" onClick={toggleMenu} className="flex items-center text-muted-foreground hover:text-foreground">
                <Globe className="mr-1 h-4 w-4" /> EN
              </Link>
              <Link href={pathname} locale="pt" onClick={toggleMenu} className="flex items-center text-muted-foreground hover:text-foreground">
                <Globe className="mr-1 h-4 w-4" /> PT
              </Link>
            </div>
          </div>
        </nav>
      )}
    </header>
  );
};

export default Header;
