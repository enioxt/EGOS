'use client'; 

import React from 'react';
import { useTranslations } from 'next-intl'; 
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLayerGroup } from '@fortawesome/free-solid-svg-icons';

const TechStackSection = () => {
  const t = useTranslations('common'); 

  return (
    <section id="tech-stack" className="content-section py-12 md:py-16 bg-background">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold font-serif mb-4 text-center">
          <FontAwesomeIcon icon={faLayerGroup} className="mr-2" /> {t('techstack_title')}
        </h2>
        <p className="section-intro text-center mb-8">
          {t('techstack_intro')}
        </p>
        {/* Placeholder for actual tech stack details */}
        <div className="tech-stack-details text-center text-muted">
          <p>{t('techstack_placeholder')}</p>
          {/* TODO: Add logos or list of technologies here */}
          {/* Example structure (replace with actual data) */}
          {/* <div className="flex justify-center space-x-8 mt-6">
            <div className="tech-item">
              <img src="/path/to/nextjs-logo.svg" alt="Next.js" className="h-12 mx-auto mb-2" />
              <p>Next.js</p>
            </div>
             <div className="tech-item">
              <img src="/path/to/python-logo.svg" alt="Python" className="h-12 mx-auto mb-2" />
              <p>Python</p>
            </div>
             <div className="tech-item">
              <img src="/path/to/docker-logo.svg" alt="Docker" className="h-12 mx-auto mb-2" />
              <p>Docker</p>
            </div>
          </div> */}
        </div>
      </div>
    </section>
  );
};

export default TechStackSection;
