// EGOS Website JavaScript
// Add interactivity here when needed.

console.log("EGOS Website JS Loaded");

document.addEventListener('DOMContentLoaded', () => {
    const langSwitchers = document.querySelectorAll('.lang-switch');
    const langContents = document.querySelectorAll('.lang-content');
    const langIndicators = document.querySelectorAll('.lang-indicator'); // Select all indicators
    const supportedLangs = ['en', 'pt', 'es', 'fr', 'de', 'ru', 'zh']; // Added new languages

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

    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            // TODO: Implement LLM API call logic
            // 1. Get input from promptGoalInput (and other future inputs)
            // 2. Construct prompt for 'quasar-alpha'
            // 3. Call backend API to interact with OpenRouter
            // 4. Display generated prompt in generatedPromptOutput
            console.log('Generate Prompt button clicked. Input:', promptGoalInput ? promptGoalInput.value : 'N/A');
            if (generatedPromptOutput) {
                generatedPromptOutput.innerHTML = '<p><i>Generating prompt... (LLM integration needed)</i></p>';
            }
        });
    }

    if (clearBtn && promptGoalInput) {
        clearBtn.addEventListener('click', () => {
            // TODO: Clear all input fields
            promptGoalInput.value = '';
            console.log('Clear button clicked.');
            if (generatedPromptOutput) {
                generatedPromptOutput.innerHTML = '<p><i>Your generated prompt will appear here...</i></p>'; // Reset output
            }
        });
    }

    if (copyBtn && generatedPromptOutput) {
        copyBtn.addEventListener('click', () => {
            // TODO: Implement copy-to-clipboard functionality
            const promptText = generatedPromptOutput.textContent || generatedPromptOutput.innerText;
            navigator.clipboard.writeText(promptText).then(() => {
                console.log('Prompt copied to clipboard!');
                // Optional: Show temporary feedback to user
            }).catch(err => {
                console.error('Failed to copy prompt: ', err);
            });
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            // TODO: Implement save functionality (e.g., to local storage or user account if available)
            console.log('Save Prompt button clicked. (Save logic needed)');
        });
    }

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

    // Add event listener for the main language selector to toggle dropdown
    const currentLangLink = document.getElementById('current-lang');
    const langOptions = document.getElementById('lang-options');

    if (currentLangLink && langOptions) {
        currentLangLink.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent navigation if it's a link
            // Toggle display: check current style or presence of a class
            const isDisplayed = langOptions.style.display === 'block';
            langOptions.style.display = isDisplayed ? 'none' : 'block';
        });

        // Optional: Close dropdown if clicking outside
        document.addEventListener('click', (e) => {
            if (!currentLangLink.contains(e.target) && !langOptions.contains(e.target)) {
                langOptions.style.display = 'none';
            }
        });
    }

    // Check for stored language preference on load
    const storedLang = localStorage.getItem('egosLangPref');
    if (storedLang && supportedLangs.includes(storedLang)) {
        setLanguage(storedLang);
    } else {
        // Default to English if no preference or preference is invalid
        setLanguage('en');
    }
});
