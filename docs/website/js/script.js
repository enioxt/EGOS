// EGOS Website JavaScript
// Add interactivity here when needed.

console.log("EGOS Website JS Loaded");

document.addEventListener('DOMContentLoaded', () => {
    const langSwitchers = document.querySelectorAll('.lang-switch');
    const langContents = document.querySelectorAll('.lang-content');
    const langIndicators = document.querySelectorAll('.lang-indicator'); // Select all indicators
    const supportedLangs = ['en', 'pt', 'es', 'fr', 'de', 'ru', 'zh']; // Added new languages

    // Function to set the language
    const setLanguage = (lang) => {
        if (!supportedLangs.includes(lang)) {
            console.warn(`Language '${lang}' not supported, defaulting to 'en'.`);
            lang = 'en';
        }

        // Hide all content sections and indicators
        langContents.forEach(content => content.style.display = 'none');
        langIndicators.forEach(indicator => indicator.style.display = 'none');

        // Show the selected language content section
        const selectedContent = document.querySelector(`.lang-content.lang-${lang}`);
        if (selectedContent) {
            selectedContent.style.display = 'block';
        }

        // Show the selected language indicator in the footer
        const selectedIndicator = document.querySelector(`.lang-indicator.lang-${lang}`);
        if (selectedIndicator) {
            selectedIndicator.style.display = 'inline'; // Show the indicator
        }

        // Update active state for switchers
        langSwitchers.forEach(switcher => {
            if (switcher.getAttribute('data-lang') === lang) {
                switcher.classList.add('active');
            } else {
                switcher.classList.remove('active');
            }
        });

        // Store preference
        localStorage.setItem('egosLangPref', lang);
        // Update HTML lang attribute (optional but good practice)
        document.documentElement.lang = lang;
    };

    // Add click listeners to switchers
    langSwitchers.forEach(switcher => {
        switcher.addEventListener('click', (e) => {
            e.preventDefault();
            const selectedLang = switcher.getAttribute('data-lang');
            setLanguage(selectedLang);
        });
    });

    // Check for stored language preference on load
    const storedLang = localStorage.getItem('egosLangPref');
    if (storedLang && supportedLangs.includes(storedLang)) {
        setLanguage(storedLang);
    } else {
        // Default to English if no preference or preference is invalid
        setLanguage('en');
    }
});
