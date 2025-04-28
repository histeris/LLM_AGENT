import re

def parse_agent_text(text_agent):
    """
    Fungsi untuk parsing text agent menjadi list of dictionary yang rapi.
    """
    if not isinstance(text_agent, str):
        return text_agent  # Kalau sudah format bagus, return apa adanya

    # Pisahkan berdasarkan nomor
    blocks = re.split(r'\n?\d+\.\s+', text_agent.strip())
    blocks = [block.strip() for block in blocks if block.strip()]  # buang kosong

    result = []
    for block in blocks:
        penyakit = {}
        lines = block.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')  # nama key jadi snake_case
                value = value.strip()
                penyakit[key] = value
        if penyakit:  # hanya append kalau ada data
            result.append(penyakit)

    return result if result else text_agent  # kalau parsing gagal, tetap return teks original
