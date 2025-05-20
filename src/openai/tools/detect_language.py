from langdetect import detect

def detect_language(text):
    try:
        lang = detect(text)
        return 'id' if lang == 'id' else 'en'
    except:
        return 'en'