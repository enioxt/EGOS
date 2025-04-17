# EGOS Website Internationalization (i18n) Conventions

This document outlines the conventions used for internationalizing the EGOS project website (`docs/index.html`).

## 1. Locale Files

- Translation strings are stored in JSON files within the `docs/locales/` directory.
- Each language has its own file, named according to its ISO 639-1 code (e.g., `en.json`, `pt.json`).
- These files contain key-value pairs, where the key corresponds to a `data-i18n` attribute in the HTML, and the value is the translated string for that language.

## 2. `data-i18n` Attributes

- HTML elements that require translation must have a `data-i18n` attribute.
- The value of the `data-i18n` attribute serves as the key in the locale JSON files.

## 3. Key Naming Convention

Keys follow a `section_element_specific` pattern:

- **`section`**: The `id` of the parent `<section>` element (e.g., `hero`, `mission`, `vision`, `principles`, `subsystems`).
- **`element`**: A descriptor of the HTML element or its content (e.g., `title`, `intro`, `text`, `item`, `cta`, `link`).
- **`specific`**: (Optional) A further qualifier to distinguish similar elements within the same section (e.g., `_art`, `_ethik`, `_cta_mission`, `_redemption_title`).

**Examples:**

- `hero_title`: The `<h2>` title within the `#hero` section.
- `vision_intro`: The introductory paragraph (`<p class="section-intro">`) in the `#vision` section.
- `principles_redemption_title`: The `<h3>` title for the 'Universal Redemption' principle card within the `#principles` section.
- `subsystems_github_link`: The common text for all 'View on GitHub' links within the `#subsystems` section.

## 4. Handling Attributes (e.g., `placeholder`, `aria-label`)

- To translate element attributes (like `placeholder` on a `<textarea>` or `aria-label` on a `<button>`), use a custom data attribute prefixed with `data-i18n-` followed by the target attribute name (e.g., `data-i18n-placeholder`, `data-i18n-aria-label`).
- The value of this custom data attribute should be the translation key to use from the locale JSON files.
- The JavaScript logic (`applyTranslations` function in `docs/js/script.js`) specifically looks for these `data-i18n-*` attributes and updates the corresponding target attribute on the element.

**Example HTML:**
```html
<textarea data-i18n-placeholder="promptgen_placeholder_goal" placeholder="Default Placeholder..."></textarea>
<button data-i18n-aria-label="nav_toggle_menu" aria-label="Default Label...">...</button>
```

**Example JS Snippet (Conceptual from `applyTranslations`):**
```javascript
document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
    const key = element.dataset.i18nPlaceholder;
    element.placeholder = translations[key] || key;
});
document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
    const key = element.dataset.i18nArialabel; // Note: camelCase conversion
    element.setAttribute('aria-label', translations[key] || key);
});
```

## 5. JavaScript Implementation

- The core logic resides in `docs/js/script.js` within the `DOMContentLoaded` event listener.
- The `fetchTranslations(lang)` function asynchronously loads the `/docs/locales/${lang}.json` file.
- The `applyTranslations(translations)` function iterates through elements with `data-i18n` attributes (updating `innerText` or `innerHTML` cautiously if the translation contains HTML) and specific `data-i18n-*` attributes (updating the corresponding element attribute like `placeholder` or `aria-label`).
- The `setLanguage(lang)` function orchestrates fetching and applying translations, updates the active language switcher UI, stores the preference in `localStorage`, and sets the `lang` attribute on the `<html>` element.
- Initial language is determined on page load based on `localStorage` preference, falling back to the browser's primary language if supported, or defaulting to 'en'.

---
*Following KOIOS standards for clear documentation.* 
