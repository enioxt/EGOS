import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';

interface PrincipleCardProps {
  icon: IconDefinition;
  titleKey: string;
  titleDefault: string;
  textKey: string;
  textDefault: string;
}

const PrincipleCard: React.FC<PrincipleCardProps> = ({ 
  icon, 
  titleKey, 
  titleDefault, 
  textKey, 
  textDefault 
}) => {
  return (
    <div className="principle-item card-hover bg-card-background p-6 rounded shadow hover:shadow-lg transition-shadow duration-300 flex flex-col items-center text-center">
      <FontAwesomeIcon icon={icon} className="text-accent mb-4 h-10 w-10" /> {/* Increased size slightly */}
      <h3 
        className="text-xl font-bold font-serif mb-2"
        data-i18n={titleKey}
      >
        {titleDefault} {/* Default text for initial rendering */}
      </h3>
      <p data-i18n={textKey}>
        {textDefault} {/* Default text for initial rendering */}
      </p>
    </div>
  );
};

export default PrincipleCard;
