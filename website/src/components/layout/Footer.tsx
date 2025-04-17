'use client';

import { Github, MessageCircle, BookOpen, Globe, Rocket, PanelRight, Heart } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-footer-background border-t border-border py-12 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">EGOS Project</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Evolving Generative Operating System - An open-source framework for conscious AI development.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Community</h3>
            <ul className="space-y-3">
              <li>
                <a 
                  href="https://github.com/enioxt/egos"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <Github className="h-4 w-4" />
                  GitHub Repository
                </a>
              </li>
              <li>
                <a 
                  href="https://t.me/ethikin"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <MessageCircle className="h-4 w-4" />
                  Telegram Community
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/enioxt/egos/discussions"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <PanelRight className="h-4 w-4" />
                  GitHub Discussions
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Resources</h3>
            <ul className="space-y-3">
              <li>
                <a 
                  href="https://github.com/enioxt/egos/wiki"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <BookOpen className="h-4 w-4" />
                  Documentation
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/enioxt/egos/blob/main/CONTRIBUTING.md"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <Heart className="h-4 w-4" />
                  Contribution Guide
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/enioxt/egos#roadmap"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <Rocket className="h-4 w-4" />
                  GitHub Roadmap
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">ETHIK Tokens</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Contribute and earn ETHIK tokens available on:
            </p>
            <ul className="space-y-3">
              <li>
                <a 
                  href="https://solscan.io/token/DsLmsjwXschqEe5EnHFvv1oi5BNGoQin6VDN81Ufpump"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <Globe className="h-4 w-4" />
                  Solana
                </a>
              </li>
              <li>
                <a 
                  href="https://basescan.org/token/0x633b346b85c4877ace4d47f7aa72c2a092136cb5"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <Globe className="h-4 w-4" />
                  Base
                </a>
              </li>
              <li>
                <a 
                  href="https://hyperscan.xyz/token/0xEFC3c015E0CD02246e6b6CD5faA89e96a71Ec1E4"
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
                >
                  <Globe className="h-4 w-4" />
                  Hyperliquid
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-border pt-8">
          <p className="text-sm text-muted-foreground text-center">
            {currentYear} EGOS Project. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
