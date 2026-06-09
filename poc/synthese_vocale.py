def generate_speech(text, voice_id="alloy", language="en"):
    """
    Simule la synthèse vocale via API (ex: OpenAI TTS ou Azure TTS).
    Supporte le format SSML.
    """
    ssml_template = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
        <voice name="{voice_id}">
            <prosody rate="medium" pitch="default">
                {text}
            </prosody>
        </voice>
    </speak>
    """
    print(f"Génération de la voix pour : {text}")
    print(f"Utilisation du SSML :\n{ssml_template}")

    return "output_dubbed.mp3"

if __name__ == "__main__":
    text = "Hello everyone, this is an automatic dubbing test."
    output = generate_speech(text, language="en")
    print(f"Fichier généré : {output}")
