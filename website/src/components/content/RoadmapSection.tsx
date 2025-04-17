'use client'; 

import React from 'react';
import { useTranslations } from 'next-intl'; 
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapSigns } from '@fortawesome/free-solid-svg-icons'; 

const RoadmapSection = () => {
  const t = useTranslations('common'); 
  const roadmapUrl = "https://github.com/orgs/enioxt/projects/1"; 

  return (
    <section id="roadmap" className="content-section py-12 md:py-16 bg-background">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold font-serif mb-4 text-center">
          <FontAwesomeIcon icon={faMapSigns} className="mr-2" /> {t('roadmap_title')}
        </h2>
        <p className="section-intro text-center mb-8">
          {t('roadmap_intro')}
        </p>
        <div className="roadmap-content text-center">
          <p className="mb-6">
            {t('roadmap_details')}
          </p>
          <a 
            href={roadmapUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="cta-button primary bg-accent hover:bg-accent-dark text-white font-bold py-3 px-8 rounded transition-colors duration-300 inline-flex items-center"
            title={t('roadmap_link_alt')}
          >
            {t('roadmap_link_text')} 
          </a>
        </div>
      </div>
    </section>
  );
};

export default RoadmapSection;
