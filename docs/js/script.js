// EGOS Website JavaScript
// Add interactivity here when needed.

console.log("EGOS Website JS Loaded");

document.addEventListener('DOMContentLoaded', () => {
    const supportedLangs = ['en', 'pt', 'es', 'fr', 'de', 'ru', 'zh']; // Ensure this matches available locale files
    let currentTranslations = {}; // To store loaded translations

    // Hamburger menu toggle
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.main-nav');

    if (hamburger && nav) {
        hamburger.addEventListener('click', () => {
            const isOpen = nav.classList.toggle('menu-open');
            hamburger.classList.toggle('open');
            hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    }

    // Expandable subsystem cards
    const expandToggles = document.querySelectorAll('.expand-toggle');

    expandToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const card = toggle.closest('.subsystem-card');
            if (card) {
                card.classList.toggle('expanded');
                const isExpanded = card.classList.contains('expanded');
                // Update aria-expanded based on actual state
                // Note: data-i18n-aria-label handles the *label* translation
                toggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
            }
        });
    });

    // Quantum Prompt Generator Button Logic (Placeholders)
    const generateBtn = document.getElementById('generate-prompt-btn');
    const clearBtn = document.getElementById('clear-prompt-btn');
    const copyBtn = document.getElementById('copy-prompt-btn');
    const saveBtn = document.getElementById('save-prompt-btn');
    const promptGoalInput = document.getElementById('prompt-goal');
    const generatedPromptOutput = document.getElementById('generated-prompt');
    const promptOutputPlaceholder = document.querySelector('#generated-prompt i[data-i18n="promptgen_output_placeholder"]'); // Specific selector for the placeholder

    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            console.log('Generate Prompt button clicked. Input:', promptGoalInput ? promptGoalInput.value : 'N/A');
            if (promptOutputPlaceholder) {
                promptOutputPlaceholder.textContent = currentTranslations['promptgen_output_generating'] || 'Generating prompt...'; // Use translation key
            }
            // TODO: Implement LLM API call logic
        });
    }

    if (clearBtn && promptGoalInput) {
        clearBtn.addEventListener('click', () => {
            promptGoalInput.value = '';
            console.log('Clear button clicked.');
            if (promptOutputPlaceholder) {
                promptOutputPlaceholder.textContent = currentTranslations['promptgen_output_placeholder'] || 'Your generated prompt will appear here... (LLM integration needed)'; // Reset with translated placeholder
            }
        });
    }

    if (copyBtn && generatedPromptOutput) {
        copyBtn.addEventListener('click', () => {
            const promptText = generatedPromptOutput.textContent || generatedPromptOutput.innerText;
            // Exclude the placeholder text if it's currently showing
            const placeholderKey = 'promptgen_output_placeholder';
            const placeholderText = currentTranslations[placeholderKey] || 'Your generated prompt will appear here...';
            if (!promptText.includes(placeholderText)) {
                navigator.clipboard.writeText(promptText.trim()).then(() => {
                    console.log('Prompt copied to clipboard!');
                    // TODO: Add user feedback (e.g., change button text temporarily)
                }).catch(err => {
                    console.error('Failed to copy prompt: ', err);
                });
            } else {
                console.log('Nothing generated to copy yet.');
            }
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            console.log('Save Prompt button clicked. (Save logic needed)');
            // TODO: Implement save functionality
        });
    }

    // --- New i18n Logic --- 

    // Function to fetch translation data
    async function fetchTranslations(lang) {
        try {
            const response = await fetch(`locales/${lang}.json`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Could not load translations for ${lang}:`, error);
            return {}; // Return empty object on error
        }
    }

    // Function to apply translations to elements
    function applyTranslations(translations) {
        if (Object.keys(translations).length === 0) return; // Don't apply if fetch failed

        // Update elements with data-i18n for innerText
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.dataset.i18n;
            // Retain child elements like <i> by updating innerHTML if needed, cautiously
            // Basic check: if translation contains HTML tags, use innerHTML
            if (translations[key]) {
                 if (/<[a-z][\s\S]*>/i.test(translations[key])) { 
                     element.innerHTML = translations[key];
                 } else {
                     element.innerText = translations[key];
                 }
            } else {
                 element.innerText = key; // Fallback to key name
                 console.warn(`Missing translation for key: ${key}`);
            }
        });

        // Update element attributes (add more as needed)
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.dataset.i18nPlaceholder;
            element.placeholder = translations[key] || key;
             if (!translations[key]) console.warn(`Missing placeholder translation for key: ${key}`);
        });

        document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
            const key = element.dataset.i18nArialabel; // Note: dataset converts kebab-case to camelCase
            element.setAttribute('aria-label', translations[key] || key);
             if (!translations[key]) console.warn(`Missing aria-label translation for key: ${key}`);
        });
        
        // Update the QPG placeholder specifically if translations loaded
        if (promptOutputPlaceholder && translations['promptgen_output_placeholder']) {
             promptOutputPlaceholder.textContent = translations['promptgen_output_placeholder'];
        }
    }

    // Function to set the language (modified)
    async function setLanguage(lang) {
        if (!supportedLangs.includes(lang)) {
            console.warn(`Language '${lang}' not supported, defaulting to 'en'.`);
            lang = 'en';
        }

        currentTranslations = await fetchTranslations(lang);
        applyTranslations(currentTranslations);

        // Update active state for switchers (assuming .lang-switch elements exist)
        document.querySelectorAll('.lang-switch').forEach(switcher => {
            if (switcher.dataset.lang === lang) {
                switcher.classList.add('active');
            } else {
                switcher.classList.remove('active');
            }
        });
        
        // Update currently selected language display if exists
        const currentLangDisplay = document.getElementById('current-lang-text');
        if (currentLangDisplay) {
            // Find the name of the selected language (assuming a structure)
            const langName = document.querySelector(`.lang-switch[data-lang="${lang}"]`)?.textContent || lang.toUpperCase();
            currentLangDisplay.textContent = langName;
        }

        // Store preference
        localStorage.setItem('egosLangPref', lang);
        // Update HTML lang attribute
        document.documentElement.lang = lang;
    };

    // --- End New i18n Logic ---

    // Event listener for language switchers (e.g., in a dropdown)
    document.querySelectorAll('.lang-switch').forEach(switcher => {
        switcher.addEventListener('click', (e) => {
            e.preventDefault();
            const selectedLang = switcher.dataset.lang;
            setLanguage(selectedLang);
            // Close dropdown if it's open
            const langOptions = document.getElementById('lang-options');
            if (langOptions) {
                langOptions.style.display = 'none';
            }
        });
    });

    // Add event listener for the main language selector toggle
    const currentLangLink = document.getElementById('current-lang');
    const langOptions = document.getElementById('lang-options');

    if (currentLangLink && langOptions) {
        currentLangLink.addEventListener('click', (e) => {
            e.preventDefault();
            const isDisplayed = langOptions.style.display === 'block';
            langOptions.style.display = isDisplayed ? 'none' : 'block';
            currentLangLink.setAttribute('aria-expanded', !isDisplayed);
        });

        // Close dropdown if clicking outside
        document.addEventListener('click', (e) => {
            if (!currentLangLink.contains(e.target) && !langOptions.contains(e.target)) {
                langOptions.style.display = 'none';
                 currentLangLink.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Initial language setup on load
    const storedLang = localStorage.getItem('egosLangPref');
    const browserLang = navigator.language.split('-')[0]; // Get primary language code (e.g., 'en' from 'en-US')
    let initialLang = 'en'; // Default

    if (storedLang && supportedLangs.includes(storedLang)) {
        initialLang = storedLang;
    } else if (supportedLangs.includes(browserLang)) {
        initialLang = browserLang; // Use browser language if supported and no preference stored
    }

    setLanguage(initialLang); // Load and apply the initial language
});
