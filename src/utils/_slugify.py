import re

SLUG_SPLITTER = "-"


def _transliterate(text):
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    return ''.join(translit_map.get(char, char) for char in text)

def _shorten(text: str, max_length: int):
    parts = text.split(SLUG_SPLITTER)
    result = ""

    if len(parts) == 1:
        return parts[:max_length]

    for part in parts:
        if result + part + len(SLUG_SPLITTER) > max_length:
            return result

        result += SLUG_SPLITTER + part

    return result

def slugify(text: str, max_length: int = None):
    text = _transliterate(text)
    text = text.lower()

    # Replace spaces and non-alphanumeric characters with hyphens
    text = re.sub(r'\s+', SLUG_SPLITTER, text)  # Replace spaces with hyphens
    text = re.sub(r'[^a-z0-9\-]', '', text)  # Remove everything except letters, digits, and hyphens

    # Remove extra hyphens
    text = re.sub(r'-+', SLUG_SPLITTER, text)  # Replace multiple hyphens with one
    text = text.strip(SLUG_SPLITTER)  # Remove hyphens at the beginning and end

    if max_length and len(text) > max_length:
        _shorten(text, max_length)

    return text
