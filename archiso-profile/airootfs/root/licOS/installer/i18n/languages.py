import os
import locale as loc


LANGUAGES = {
    "en": "English",
    "zh": "中文 (简体)",
    "zh_TW": "中文 (繁體)",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "pt": "Português",
    "ru": "Русский",
    "ar": "العربية",
    "it": "Italiano",
}


LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Chinese (Simplified)",
    "zh_TW": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "it": "Italian",
}


LOCALE_TO_LANG = {
    "en": "en", "en_US": "en", "en_GB": "en",
    "zh": "zh", "zh_CN": "zh", "zh_SG": "zh",
    "zh_TW": "zh_TW", "zh_HK": "zh_TW",
    "ja": "ja", "ja_JP": "ja",
    "ko": "ko", "ko_KR": "ko",
    "fr": "fr", "fr_FR": "fr", "fr_CA": "fr",
    "de": "de", "de_DE": "de", "de_AT": "de", "de_CH": "de",
    "es": "es", "es_ES": "es", "es_MX": "es",
    "pt": "pt", "pt_BR": "pt", "pt_PT": "pt",
    "ru": "ru", "ru_RU": "ru",
    "ar": "ar", "ar_SA": "ar",
    "it": "it", "it_IT": "it", "it_CH": "it",
}


def detect_system_language() -> str:
    try:
        sys_lang, _ = loc.getdefaultlocale()
        if sys_lang:
            base = sys_lang.split(".")[0]
            if base in LOCALE_TO_LANG:
                return LOCALE_TO_LANG[base]
        lang = os.environ.get("LANG", "en_US.UTF-8")
        base = lang.split(".")[0]
        if base in LOCALE_TO_LANG:
            return LOCALE_TO_LANG[base]
    except Exception:
        pass
    return "en"


def get_locale_for_lang(lang_code: str) -> str:
    mapping = {
        "en": "en_US.UTF-8",
        "zh": "zh_CN.UTF-8",
        "zh_TW": "zh_TW.UTF-8",
        "ja": "ja_JP.UTF-8",
        "ko": "ko_KR.UTF-8",
        "fr": "fr_FR.UTF-8",
        "de": "de_DE.UTF-8",
        "es": "es_ES.UTF-8",
        "pt": "pt_BR.UTF-8",
        "ru": "ru_RU.UTF-8",
        "ar": "ar_SA.UTF-8",
        "it": "it_IT.UTF-8",
    }
    return mapping.get(lang_code, "en_US.UTF-8")
