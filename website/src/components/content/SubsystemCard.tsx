'use client'; // Required for useState hook

import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';

interface SubsystemCardProps {
  titleKey: string;        // Key for translation
  titleDefault: string;  // Default/translated title text
  descriptionKey: string;
  descriptionDefault: string;
  detailsKey: string;
  detailsDefault: string;
}

const SubsystemCard: React.FC<SubsystemCardProps> = ({
  titleKey,
  titleDefault,
  descriptionKey,
  descriptionDefault,
  detailsKey,
  detailsDefault,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="subsystem-card bg-gradient-to-br from-background to-background-alt p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
      <button 
        onClick={toggleExpand} 
        className="w-full text-left flex justify-between items-center focus:outline-none" 
        aria-expanded={isExpanded}
        aria-controls={`details-${titleKey}`} // For accessibility
      >
        <h3 className="text-xl font-semibold font-serif text-primary" data-i18n={titleKey}>{titleDefault}</h3>
        <FontAwesomeIcon 
          icon={isExpanded ? faChevronUp : faChevronDown} 
          className="text-accent transition-transform duration-300 transform" 
          style={{ transform: isExpanded ? 'rotate(0deg)' : 'rotate(0deg)' }} // Keeps icon static, can add rotation if desired
        />
      </button>
      <p className="text-text-secondary mt-2 mb-4" data-i18n={descriptionKey}>{descriptionDefault}</p>
      {isExpanded && (
        <div 
          id={`details-${titleKey}`} 
          className="subsystem-details mt-4 pt-4 border-t border-primary-light text-text"
          data-i18n={detailsKey}
        >
          {detailsDefault}
        </div>
      )}
    </div>
  );
};

export default SubsystemCard;
