import React from 'react';

export const WaveSvg = ({ className = "" }: { className?: string }) => {
  return (
    <svg className={className} viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
      <path 
        d="M0,80 C240,120 480,40 720,70 C960,100 1200,30 1440,80 L1440,120 L0,120 Z" 
        fill="#F1FFD4"
        opacity="0.7"
      />
      <path 
        d="M0,70 C240,110 480,30 720,60 C960,90 1200,20 1440,70 L1440,120 L0,120 Z" 
        fill="#E8D9F0"
        opacity="0.5"
      />
    </svg>
  );
};
