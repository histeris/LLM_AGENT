import re

def clean_key(key):
    # Hilangkan simbol markdown dan ubah ke snake_case
    key = re.sub(r'[^a-zA-Z0-9 ]', '', key)  # hapus simbol seperti -, *, _
    key = key.strip().lower().replace(' ', '_')
    return key

def parse_agent_text(text_agent):
    """
    Fungsi untuk parsing text agent menjadi list of dictionary yang rapi.
    """
    if not isinstance(text_agent, str):
        return text_agent

    blocks = re.split(r'\n?\d+\.\s+', text_agent.strip())
    blocks = [block.strip() for block in blocks if block.strip()]

    result = []
    for block in blocks:
        penyakit = {}
        lines = block.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = clean_key(key)
                value = value.strip()
                penyakit[key] = value
        if penyakit:
            result.append(penyakit)

    return result if result else text_agent