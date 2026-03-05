import re

# Компилируем регулярки один раз при запуске
PHONE_PATTERN = re.compile(r'(?:(?:\+7|8|7)[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
CLEAN_PHONE = re.compile(r'[\s\-\(\)]')
NORMALIZE_SEP = re.compile(r'[,\n\r]+')
EXTRA_SPACES = re.compile(r'\s+')


def safe_str(value) -> str:
    """Защита от None — возвращает пустую строку вместо None"""
    return str(value) if value else ""


def format_contacts(contacts_text: str) -> str:
    """
    Преобразует номера телефонов в кликабельные ссылки tel:
    Оптимизированная версия с предварительной компиляцией regex
    """
    if not contacts_text:
        return "—"

    # Нормализуем разделители
    normalized = NORMALIZE_SEP.sub(' ', contacts_text)
    normalized = EXTRA_SPACES.sub(' ', normalized)

    def replace_phone(match):
        phone = match.group(0)
        clean_phone = CLEAN_PHONE.sub('', phone)

        if not clean_phone.startswith('+'):
            if clean_phone.startswith('8'):
                clean_phone = '+7' + clean_phone[1:]
            elif clean_phone.startswith('7'):
                clean_phone = '+' + clean_phone
            else:
                clean_phone = '+7' + clean_phone

        return f'<a href="tel:{clean_phone}">{phone}</a>'

    return PHONE_PATTERN.sub(replace_phone, normalized)


def format_prezentaciya(link: str) -> str:
    """Преобразует ссылку в кликабельную"""
    if not link:
        return "—"
    return f'<a href="{link}">📎 Открыть презентацию</a>'