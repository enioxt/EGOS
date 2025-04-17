
import React from 'react';
import { Github, Twitter, Slack, BookOpen, Map, FileText } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-egos-black text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-serif text-2xl font-medium mb-4">EGOS</h3>
            <p className="text-gray-400 text-sm mb-4">
              Empowering developers, researchers, artists, and organizations to build conscious, trustworthy, and beautiful AI systems.
            </p>
          </div>
          
          <div>
            <h4 className="font-medium mb-4 text-egos-blue">Project</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors flex items-center"><BookOpen className="w-4 h-4 mr-2" /> Documentation</a></li>
              <li><a href="#principles" className="text-gray-400 hover:text-white text-sm transition-colors flex items-center"><FileText className="w-4 h-4 mr-2" /> Principles</a></li>
              <li><a href="#roadmap" className="text-gray-400 hover:text-white text-sm transition-colors flex items-center"><Map className="w-4 h-4 mr-2" /> Roadmap</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-4 text-egos-pink">Community</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors flex items-center"><Github className="w-4 h-4 mr-2" /> GitHub</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors flex items-center"><Twitter className="w-4 h-4 mr-2" /> Twitter</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors flex items-center"><Slack className="w-4 h-4 mr-2" /> Discord</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-4 text-egos-lime">Languages</h4>
            <ul className="space-y-2 flex gap-4">
              <li><a href="#" className="text-white font-medium text-sm">English</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Português</a></li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 text-sm">© 2025 EGOS Project. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy</a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms</a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">Governance</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
