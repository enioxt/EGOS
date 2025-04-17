import { useTranslations } from 'next-intl'; // Import useTranslations
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faEye, faHeartCircleCheck, faRecycle, faCubes, faWandMagicSparkles,
  // Principle Icons
  faClock, faLock, faUniversalAccess, faHeart, faHandshake, faProjectDiagram, 
  faMapMarkedAlt, faSeedling, faBalanceScale
} from '@fortawesome/free-solid-svg-icons';

// Import content components
import PrincipleCard from '@/components/content/PrincipleCard';
import SubsystemCard from '@/components/content/SubsystemCard';
import QuantumPromptGenerator from '@/components/features/QuantumPromptGenerator';
import TechStackSection from '@/components/content/TechStackSection';
import RoadmapSection from '@/components/content/RoadmapSection';

export default function Home() {
  const t = useTranslations('common'); // Initialize translations for 'common' namespace

  return (
    <>
      {/* Hero Section */}
      <section className="hero-section bg-gradient-to-r from-primary to-primary-dark text-text-on-primary py-20 md:py-32 text-center relative overflow-hidden">
         {/* Optional: Add subtle background pattern/texture */}
         <div className="container mx-auto px-4 relative z-10">
           <h1 className="text-4xl md:text-5xl font-bold font-serif mb-4" data-i18n="hero_title">{t('hero_title')}</h1>
           <p className="text-lg md:text-xl mb-8" data-i18n="hero_subtitle">{t('hero_subtitle')}</p>
           <div className="cta-buttons">
             <a href="#vision" className="cta-button primary bg-accent hover:bg-accent-dark text-white font-bold py-3 px-8 rounded transition-colors duration-300 mr-4" data-i18n="hero_cta_learn">
               {t('hero_cta_learn')}
             </a>
             <a href="https://github.com/enioxt/EGOS" target="_blank" rel="noopener noreferrer" className="cta-button secondary bg-white hover:bg-gray-200 text-primary font-bold py-3 px-6 rounded transition-colors duration-300 inline-flex items-center" data-i18n="hero_cta_github">
               {/* Add GitHub icon here if desired */}
               {t('hero_cta_github')}
             </a>
           </div>
         </div>
       </section>

      {/* Vision Section */}
      <section id="vision" className="content-section py-12 md:py-16 bg-background-alt">
         <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold font-serif mb-4" data-i18n="vision_title">
             <FontAwesomeIcon icon={faEye} className="mr-2" /> {t('vision_title')}
           </h2>
           <p className="max-w-3xl mx-auto" data-i18n="vision_intro">
             {t('vision_intro')}
           </p>
         </div>
       </section>

      {/* Principles Section - Updated with Component */}
      <section id="principles" className="content-section py-12 md:py-16 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold font-serif mb-4 text-center" data-i18n="principles_title">
            <FontAwesomeIcon icon={faHeartCircleCheck} className="mr-2" /> {t('principles_title')}
          </h2>
          <p className="section-intro text-center mb-8" data-i18n="principles_intro">{t('principles_intro')}</p>
          <div className="principles-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Pass t() function results or keys directly */}
            <PrincipleCard 
              icon={faRecycle} 
              titleKey="principles_redemption_title"
              titleDefault={t('principles_redemption_title')}
              textKey="principles_redemption_text"
              textDefault={t('principles_redemption_text')}
            />
            <PrincipleCard 
              icon={faClock} 
              titleKey="principles_temporality_title"
              titleDefault={t('principles_temporality_title')}
              textKey="principles_temporality_text"
              textDefault={t('principles_temporality_text')}
            />
             <PrincipleCard 
              icon={faLock} 
              titleKey="principles_privacy_title"
              titleDefault={t('principles_privacy_title')}
              textKey="principles_privacy_text"
              textDefault={t('principles_privacy_text')}
            />
             <PrincipleCard 
              icon={faUniversalAccess} 
              titleKey="principles_accessibility_title"
              titleDefault={t('principles_accessibility_title')}
              textKey="principles_accessibility_text"
              textDefault={t('principles_accessibility_text')}
            />
             <PrincipleCard 
              icon={faHeart} 
              titleKey="principles_love_title"
              titleDefault={t('principles_love_title')}
              textKey="principles_love_text"
              textDefault={t('principles_love_text')}
            />
             <PrincipleCard 
              icon={faHandshake} 
              titleKey="principles_trust_title"
              titleDefault={t('principles_trust_title')}
              textKey="principles_trust_text"
              textDefault={t('principles_trust_text')}
            />
             <PrincipleCard 
              icon={faBalanceScale} 
              titleKey="principles_ethics_title"
              titleDefault={t('principles_ethics_title')}
              textKey="principles_ethics_text"
              textDefault={t('principles_ethics_text')}
            />
             <PrincipleCard 
              icon={faProjectDiagram} 
              titleKey="principles_modularity_title"
              titleDefault={t('principles_modularity_title')}
              textKey="principles_modularity_text"
              textDefault={t('principles_modularity_text')}
            />
             <PrincipleCard 
              icon={faMapMarkedAlt} 
              titleKey="principles_cartography_title"
              titleDefault={t('principles_cartography_title')}
              textKey="principles_cartography_text"
              textDefault={t('principles_cartography_text')}
            />
             <PrincipleCard 
              icon={faSeedling} 
              titleKey="principles_preservation_title"
              titleDefault={t('principles_preservation_title')}
              textKey="principles_preservation_text"
              textDefault={t('principles_preservation_text')}
            />
          </div>
        </div>
      </section>

      {/* Subsystems Section - Updated with Component */}
      <section id="subsystems" className="content-section py-12 md:py-16 bg-background-alt">
        <div className="container mx-auto px-4">
           <h2 className="text-3xl font-bold font-serif mb-4 text-center" data-i18n="subsystems_title">
             <FontAwesomeIcon icon={faCubes} className="mr-2" /> {t('subsystems_title')}
           </h2>
           <p className="section-intro text-center mb-8" data-i18n="subsystems_intro">{t('subsystems_intro')}</p>
           <div className="subsystems-grid grid grid-cols-1 md:grid-cols-2 gap-8">
             <SubsystemCard 
               titleKey="subsystems_mycelium_title"
               titleDefault={t('subsystems_mycelium_title')}
               descriptionKey="subsystems_mycelium_desc"
               descriptionDefault={t('subsystems_mycelium_desc')}
               detailsKey="subsystems_mycelium_details"
               detailsDefault={t('subsystems_mycelium_details')}
             />
             <SubsystemCard 
               titleKey="subsystems_synapse_title"
               titleDefault={t('subsystems_synapse_title')}
               descriptionKey="subsystems_synapse_desc"
               descriptionDefault={t('subsystems_synapse_desc')}
               detailsKey="subsystems_synapse_details"
               detailsDefault={t('subsystems_synapse_details')}
             />
             <SubsystemCard 
               titleKey="subsystems_koios_title"
               titleDefault={t('subsystems_koios_title')}
               descriptionKey="subsystems_koios_desc"
               descriptionDefault={t('subsystems_koios_desc')}
               detailsKey="subsystems_koios_details"
               detailsDefault={t('subsystems_koios_details')}
             />
             <SubsystemCard 
               titleKey="subsystems_ethik_title"
               titleDefault={t('subsystems_ethik_title')}
               descriptionKey="subsystems_ethik_desc"
               descriptionDefault={t('subsystems_ethik_desc')}
               detailsKey="subsystems_ethik_details"
               detailsDefault={t('subsystems_ethik_details')}
             />
             <SubsystemCard 
               titleKey="subsystems_cronos_title"
               titleDefault={t('subsystems_cronos_title')}
               descriptionKey="subsystems_cronos_desc"
               descriptionDefault={t('subsystems_cronos_desc')}
               detailsKey="subsystems_cronos_details"
               detailsDefault={t('subsystems_cronos_details')}
             />
              <SubsystemCard 
               titleKey="subsystems_coruja_title"
               titleDefault={t('subsystems_coruja_title')}
               descriptionKey="subsystems_coruja_desc"
               descriptionDefault={t('subsystems_coruja_desc')}
               detailsKey="subsystems_coruja_details"
               detailsDefault={t('subsystems_coruja_details')}
             />
           </div>
        </div>
      </section>

      {/* Tech Stack Section - Updated with Component */}
      <TechStackSection /> 
      {/* Note: TechStackSection needs internal translation using useTranslations */}

      {/* Quantum Prompt Generator Section - Updated with Component */}
      <section id="prompt-generator" className="content-section py-12 md:py-16 bg-background-alt">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold font-serif mb-4 text-center" data-i18n="promptgen_title">
            <FontAwesomeIcon icon={faWandMagicSparkles} className="mr-2" /> {t('promptgen_title')}
          </h2>
          <p className="section-intro text-center mb-8" data-i18n="promptgen_intro">{t('promptgen_intro')}</p>
          <QuantumPromptGenerator /> 
          {/* Note: QuantumPromptGenerator needs internal translation using useTranslations */}
        </div>
      </section>

      {/* Roadmap Section - Updated with Component */}
      <RoadmapSection />
      {/* Note: RoadmapSection needs internal translation using useTranslations */}

    </>
  );
}
