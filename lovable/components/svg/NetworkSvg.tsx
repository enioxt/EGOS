
import React from 'react';

export const NetworkSvg = ({ className = "" }: { className?: string }) => {
  return (
    <svg className={className} viewBox="0 0 500 400" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g className="animate-draw" strokeWidth="2" stroke="#00AEEF" strokeDasharray="1000" strokeDashoffset="1000">
        <circle cx="250" cy="200" r="80" opacity="0.6" fill="none" />
        <circle cx="250" cy="200" r="120" opacity="0.3" fill="none" />
        <circle cx="250" cy="200" r="160" opacity="0.1" fill="none" />
      </g>
      
      {/* Nodes */}
      <g className="animate-pulse-slow">
        <circle cx="250" cy="120" r="15" fill="#E8D9F0" />
        <circle cx="180" cy="180" r="12" fill="#FFB3C1" />
        <circle cx="320" cy="180" r="12" fill="#F1FFD4" />
        <circle cx="250" cy="250" r="18" fill="#00AEEF" />
        <circle cx="180" cy="240" r="10" fill="#A5E887" />
        <circle cx="320" cy="240" r="10" fill="#FFA500" />
        
        {/* Central node */}
        <circle cx="250" cy="200" r="25" fill="#4B0055" />
      </g>
      
      {/* Connections */}
      <g strokeWidth="2" stroke="#FAFAFA">
        <line x1="250" y1="125" x2="250" y2="175" className="animate-draw" strokeDasharray="1000" strokeDashoffset="1000" />
        <line x1="192" y1="180" x2="225" y2="200" className="animate-draw" strokeDasharray="1000" strokeDashoffset="1000" />
        <line x1="308" y1="180" x2="275" y2="200" className="animate-draw" strokeDasharray="1000" strokeDashoffset="1000" />
        <line x1="250" y1="225" x2="250" y2="240" className="animate-draw" strokeDasharray="1000" strokeDashoffset="1000" />
        <line x1="190" y1="240" x2="225" y2="200" className="animate-draw" strokeDasharray="1000" strokeDashoffset="1000" />
        <line x1="310" y1="240" x2="275" y2="200" className="animate-draw" strokeDasharray="1000" strokeDashoffset="1000" />
      </g>
    </svg>
  );
};
