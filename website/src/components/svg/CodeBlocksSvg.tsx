import React from 'react';

export const CodeBlocksSvg = ({ className = "" }: { className?: string }) => {
  return (
    <svg className={className} viewBox="0 0 500 400" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Code Block 1 */}
      <g className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <rect x="80" y="120" width="150" height="80" rx="4" fill="#00AEEF" opacity="0.2" />
        <text x="100" y="150" fill="#00AEEF" fontFamily="monospace" fontSize="12">
          <tspan x="100" y="150">function synapse()</tspan>
          <tspan x="100" y="170">{"  return modular();"}</tspan>
          <tspan x="100" y="190">{"}"}</tspan>
        </text>
      </g>
      
      {/* Code Block 2 */}
      <g className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
        <rect x="250" y="100" width="160" height="100" rx="4" fill="#F1FFD4" opacity="0.6" />
        <text x="270" y="130" fill="#0A0A0A" fontFamily="monospace" fontSize="12">
          <tspan x="270" y="130">class Ethik</tspan>
          <tspan x="270" y="150">{"  validate() {"}</tspan>
          <tspan x="270" y="170">{"    return true;"}</tspan>
          <tspan x="270" y="190">{"  }"}</tspan>
        </text>
      </g>
      
      {/* Code Block 3 */}
      <g className="animate-fade-in" style={{ animationDelay: '0.6s' }}>
        <rect x="100" y="220" width="140" height="100" rx="4" fill="#FFB3C1" opacity="0.4" />
        <text x="120" y="250" fill="#0A0A0A" fontFamily="monospace" fontSize="12">
          <tspan x="120" y="250">import</tspan>
          <tspan x="120" y="270">{"  Mycelium,"}</tspan>
          <tspan x="120" y="290">{"  Koios"}</tspan>
          <tspan x="120" y="310">{"from 'egos';"}</tspan>
        </text>
      </g>
      
      {/* Code Block 4 */}
      <g className="animate-fade-in" style={{ animationDelay: '0.8s' }}>
        <rect x="260" y="220" width="150" height="80" rx="4" fill="#A5E887" opacity="0.4" />
        <text x="280" y="250" fill="#0A0A0A" fontFamily="monospace" fontSize="12">
          <tspan x="280" y="250">const atlas = new</tspan>
          <tspan x="280" y="270">  Atlas()</tspan>
          <tspan x="280" y="290">atlas.connect()</tspan>
        </text>
      </g>
      
      {/* Connecting Lines */}
      <g stroke="#4B0055" strokeWidth="2" strokeDasharray="5,5" className="animate-draw">
        <path d="M155 200 L155 220" />
        <path d="M230 150 L250 150" />
        <path d="M320 200 L320 220" />
        <path d="M240 270 L260 270" />
      </g>
    </svg>
  );
};
