import React from 'react';

interface IconProps {
  className?: string;
}

export const InfinityIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path 
      d="M32 24C32 19.582 28.418 16 24 16C19.582 16 16 19.582 16 24C16 28.418 19.582 32 24 32C28.418 32 32 28.418 32 24Z" 
      fill="#FFB3C1" 
    />
    <path 
      d="M16 16C10.477 16 6 20.477 6 26C6 31.523 10.477 36 16 36C18.155 36 20.145 35.296 21.766 34.108C21.258 32.218 21 30.138 21 28C21 25.862 21.258 23.782 21.766 21.892C20.145 20.704 18.155 20 16 20C12.686 20 10 22.686 10 26C10 29.314 12.686 32 16 32" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      strokeLinecap="round" 
    />
    <path 
      d="M32 16C37.523 16 42 20.477 42 26C42 31.523 37.523 36 32 36C29.845 36 27.855 35.296 26.234 34.108C26.742 32.218 27 30.138 27 28C27 25.862 26.742 23.782 26.234 21.892C27.855 20.704 29.845 20 32 20C35.314 20 38 22.686 38 26C38 29.314 35.314 32 32 32" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      strokeLinecap="round" 
    />
  </svg>
);

export const HeartIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#A5E887" opacity="0.5" />
    <path 
      d="M24 34L21.08 31.36C16.4 27.12 13.5 24.48 13.5 21.2C13.5 18.56 15.56 16.5 18.2 16.5C19.68 16.5 21.12 17.18 22 18.26C22.88 17.18 24.32 16.5 25.8 16.5C28.44 16.5 30.5 18.56 30.5 21.2C30.5 24.48 27.6 27.12 22.92 31.38L24 34Z" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="#FFB3C1" 
    />
  </svg>
);

export const ShieldIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#00AEEF" opacity="0.3" />
    <path 
      d="M24 36C24 36 34 32 34 24V15L24 12L14 15V24C14 32 24 36 24 36Z" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <path 
      d="M21 24L23 26L27 22" 
      stroke="#4B0055" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
    />
  </svg>
);

export const ClockIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#F1FFD4" />
    <circle cx="24" cy="24" r="12" stroke="#0A0A0A" strokeWidth="2" fill="none" />
    <path d="M24 18V24L28 26" stroke="#0A0A0A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const EyeIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#E8D9F0" opacity="0.7" />
    <path 
      d="M24 18C16 18 12 24 12 24C12 24 16 30 24 30C32 30 36 24 36 24C36 24 32 18 24 18Z" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <circle cx="24" cy="24" r="4" stroke="#0A0A0A" strokeWidth="2" fill="#FFA500" opacity="0.7" />
  </svg>
);

export const GlobeIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#FFB3C1" opacity="0.3" />
    <circle cx="24" cy="24" r="10" stroke="#0A0A0A" strokeWidth="2" fill="none" />
    <path d="M14 24H34" stroke="#0A0A0A" strokeWidth="2" />
    <path d="M24 14V34" stroke="#0A0A0A" strokeWidth="2" />
    <path 
      d="M24 14C27.5 17.5 27.5 30.5 24 34" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <path 
      d="M24 14C20.5 17.5 20.5 30.5 24 34" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
  </svg>
);

export const PuzzleIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#A5E887" opacity="0.5" />
    <path 
      d="M20 14H28V17C28 18.1046 28.8954 19 30 19C31.1046 19 32 18.1046 32 17V14H34C35.1046 14 36 14.8954 36 16V18H33C31.8954 18 31 18.8954 31 20C31 21.1046 31.8954 22 33 22H36V26H33C31.8954 26 31 26.8954 31 28C31 29.1046 31.8954 30 33 30H36V32C36 33.1046 35.1046 34 34 34H32V31C32 29.8954 31.1046 29 30 29C28.8954 29 28 29.8954 28 31V34H24V31C24 29.8954 23.1046 29 22 29C20.8954 29 20 29.8954 20 31V34H16C14.8954 34 14 33.1046 14 32V30H17C18.1046 30 19 29.1046 19 28C19 26.8954 18.1046 26 17 26H14V24H17C18.1046 24 19 23.1046 19 22C19 20.8954 18.1046 20 17 20H14V16C14 14.8954 14.8954 14 16 14H20Z" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="#00AEEF" 
      fillOpacity="0.3" 
    />
  </svg>
);

export const MapIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#FFA500" opacity="0.3" />
    <path 
      d="M18 34L8 29V15L18 20M18 34L30 29M18 34V20M30 29L40 34V20L30 15M30 29V15M30 15L18 20" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
  </svg>
);

export const TreeIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#F1FFD4" />
    <path 
      d="M24 36V22" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
    />
    <path 
      d="M18 28L24 22L30 28" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <path 
      d="M16 22L24 14L32 22" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <path 
      d="M13 16L24 6L35 16" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="#A5E887" 
      fillOpacity="0.7"
    />
  </svg>
);

export const BrainIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#E8D9F0" opacity="0.7" />
    <path 
      d="M24 32H20C15.582 32 12 28.418 12 24C12 19.582 15.582 16 20 16H28C32.418 16 36 19.582 36 24C36 28.418 32.418 32 28 32" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <path 
      d="M20 24C20 22.895 19.105 22 18 22C16.895 22 16 22.895 16 24C16 25.105 16.895 26 18 26" 
      stroke="#4B0055" 
      strokeWidth="2" 
    />
    <path 
      d="M28 24C28 22.895 28.895 22 30 22C31.105 22 32 22.895 32 24C32 25.105 31.105 26 30 26" 
      stroke="#4B0055" 
      strokeWidth="2" 
    />
    <path 
      d="M20 28C20 26.895 20.895 26 22 26C23.105 26 24 26.895 24 28C24 29.105 23.105 30 22 30" 
      stroke="#4B0055" 
      strokeWidth="2" 
    />
    <path 
      d="M24 20C24 18.895 24.895 18 26 18C27.105 18 28 18.895 28 20C28 21.105 27.105 22 26 22" 
      stroke="#4B0055" 
      strokeWidth="2" 
    />
    <path 
      d="M20 20C20 18.895 19.105 18 18 18C16.895 18 16 18.895 16 20" 
      stroke="#4B0055" 
      strokeWidth="2" 
    />
  </svg>
);

export const ChatIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#FFB3C1" opacity="0.4" />
    <path 
      d="M34 28C34 29.1046 33.1046 30 32 30H20L14 36V18C14 16.8954 14.8954 16 16 16H32C33.1046 16 34 16.8954 34 18V28Z" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="#00AEEF" 
      fillOpacity="0.1" 
    />
    <path 
      d="M19 22H29" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      strokeLinecap="round" 
    />
    <path 
      d="M19 26H25" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      strokeLinecap="round" 
    />
  </svg>
);

export const DatabaseIcon = ({ className }: IconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#FFA500" opacity="0.2" />
    <ellipse cx="24" cy="18" rx="8" ry="4" stroke="#0A0A0A" strokeWidth="2" fill="none" />
    <path 
      d="M16 26C16 28 19.6 30 24 30C28.4 30 32 28 32 26" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      fill="none" 
    />
    <path 
      d="M16 18V30" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
    />
    <path 
      d="M32 18V30" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
    />
  </svg>
);
