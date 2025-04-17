'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl'; // Import useTranslations
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faWandMagicSparkles, faCopy, faCheck } from '@fortawesome/free-solid-svg-icons';

// Placeholder function - Replace with actual generation logic
const generatePrompt = (complexity: number, context: string, style: string, language: string) => {
  console.log('Generating prompt with:', { complexity, context, style, language }); // Log input for now
  // Example structure - adapt based on real generation logic
  return `Quantum-inspired prompt (Complexity: ${complexity}, Context: ${context}, Style: ${style}, Lang: ${language}) exploring the concept of interconnectedness.`; 
};

const QuantumPromptGenerator: React.FC = () => {
  const t = useTranslations('common'); // Initialize translations

  const [complexity, setComplexity] = useState(5); // Default value
  const [context, setContext] = useState('general'); // Default value
  const [style, setStyle] = useState('creative'); // Default value
  const [language, setLanguage] = useState('en'); // Default value
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = () => {
    const prompt = generatePrompt(complexity, context, style, language);
    setGeneratedPrompt(prompt);
    setCopied(false); // Reset copied state when new prompt generated
  };

  const handleCopy = () => {
    if (generatedPrompt) {
      navigator.clipboard.writeText(generatedPrompt)
        .then(() => {
          setCopied(true);
          // Reset icon after a short delay
          setTimeout(() => setCopied(false), 2000);
        })
        .catch(err => console.error('Failed to copy:', err));
    }
  };

  return (
    <div className="quantum-prompt-generator bg-card-background p-6 rounded shadow">
      {/* Input Controls */}
      <div className="generator-controls grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Complexity Slider */}
        <div className="control-group">
          <label htmlFor="complexity-slider" className="block text-sm font-medium text-text-secondary mb-1" data-i18n="promptgen_complexity_label">{t('promptgen_complexity_label')} {complexity}</label>
          <input 
            id="complexity-slider"
            type="range" 
            min="1" 
            max="10" 
            value={complexity} 
            onChange={(e) => setComplexity(Number(e.target.value))}
            className="w-full h-2 bg-primary rounded-lg appearance-none cursor-pointer range-lg accent-accent"
          />
        </div>

        {/* Context Select */}
        <div className="control-group">
          <label htmlFor="context-select" className="block text-sm font-medium text-text-secondary mb-1" data-i18n="promptgen_context_label">{t('promptgen_context_label')}</label>
          <select 
            id="context-select" 
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-accent focus:border-accent bg-input-background text-text"
          >
            <option value="general" data-i18n="promptgen_context_general">{t('promptgen_context_general')}</option>
            <option value="technical" data-i18n="promptgen_context_technical">{t('promptgen_context_technical')}</option>
            <option value="philosophical" data-i18n="promptgen_context_philosophical">{t('promptgen_context_philosophical')}</option>
            <option value="artistic" data-i18n="promptgen_context_artistic">{t('promptgen_context_artistic')}</option>
          </select>
        </div>

        {/* Style Select */}
        <div className="control-group">
          <label htmlFor="style-select" className="block text-sm font-medium text-text-secondary mb-1" data-i18n="promptgen_style_label">{t('promptgen_style_label')}</label>
          <select 
            id="style-select" 
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-accent focus:border-accent bg-input-background text-text"
          >
            <option value="creative" data-i18n="promptgen_style_creative">{t('promptgen_style_creative')}</option>
            <option value="formal" data-i18n="promptgen_style_formal">{t('promptgen_style_formal')}</option>
            <option value="poetic" data-i18n="promptgen_style_poetic">{t('promptgen_style_poetic')}</option>
            <option value="concise" data-i18n="promptgen_style_concise">{t('promptgen_style_concise')}</option>
          </select>
        </div>

        {/* Language Select (Placeholder - Link to main language switcher later) */}
        <div className="control-group">
          <label htmlFor="language-select" className="block text-sm font-medium text-text-secondary mb-1" data-i18n="promptgen_language_label">{t('promptgen_language_label')}</label>
          <select 
            id="language-select" 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-accent focus:border-accent bg-input-background text-text"
            disabled // Disable for now, sync with global state later
          >
            <option value="en">English</option>
            <option value="pt">Português</option>
          </select>
        </div>
      </div>

      {/* Generate Button */}
      <div className="text-center mb-6">
        <button 
          onClick={handleGenerate}
          className="generate-button bg-accent hover:bg-accent-dark text-white font-bold py-2 px-6 rounded transition-colors duration-300 inline-flex items-center"
          data-i18n="promptgen_generate_button"
        >
          <FontAwesomeIcon icon={faWandMagicSparkles} className="mr-2" /> {t('promptgen_generate_button')}
        </button>
      </div>

      {/* Output Area */}
      {generatedPrompt && (
        <div className="output-area mt-4 p-4 bg-output-background rounded border border-primary-light relative">
          <p className="text-text" id="generated-prompt-text">{generatedPrompt}</p>
          <button 
            onClick={handleCopy}
            className={`copy-button absolute top-2 right-2 p-1 rounded ${copied ? 'text-green-500' : 'text-gray-500 hover:text-primary'} transition-colors`}
            aria-label="Copy prompt"
            data-i18n-aria-label="promptgen_copy_button_label"
          >
            <FontAwesomeIcon icon={copied ? faCheck : faCopy} />
          </button>
        </div>
      )}
    </div>
  );
};

export default QuantumPromptGenerator;
