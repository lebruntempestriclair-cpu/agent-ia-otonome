def translate_text(text, target_lang="en"):
    """
    Simule une traduction via API (ex: DeepL ou Google Translate).
    """
    print(f"Traduction du texte : '{text}' vers '{target_lang}'")

    # Simulation de traduction
    translations = {
        "en": "Hello everyone, this is an automatic dubbing test.",
        "es": "Hola a todos, esta es una prueba de doblaje automático."
    }

    translated = translations.get(target_lang, "Translation not available")

    return {
        "original": text,
        "translated": translated,
        "source_lang": "fr",
        "target_lang": target_lang
    }

if __name__ == "__main__":
    text_to_translate = "Bonjour tout le monde, ceci est un test de doublage automatique."
    result = translate_text(text_to_translate, "en")
    print(f"Résultat : {result['translated']}")
