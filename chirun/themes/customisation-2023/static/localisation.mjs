import translations from "./translations.mjs";

window.gettext = window._ = function(key) {
    return translations[key] || key;
}
