from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard():
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Найти по названию", callback_data="find_by_name")],
        [InlineKeyboardButton(text="🏢 Поиск по застройщику", callback_data="find_by_builder")],
        [InlineKeyboardButton(text="📋 Показать список ЖК", callback_data="show_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="📧 Обратная связь", callback_data="feedback")]
    ])


def get_zhk_list_keyboard(zhk_list, page=0):
    """Список ЖК с пагинацией"""
    buttons = []
    items_per_page = 6
    start = page * items_per_page
    end = start + items_per_page
    current_page_items = zhk_list[start:end]

    for zhk in current_page_items:
        buttons.append([InlineKeyboardButton(text=zhk, callback_data=f"zhk|{zhk}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page|{page - 1}"))
    if end < len(zhk_list):
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page|{page + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_detail_keyboard(zhk_name: str):
    """Клавиатура для конкретного ЖК"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Все контакты", callback_data=f"contacts|{zhk_name}")],
        [InlineKeyboardButton(text="🏦 Банк", callback_data=f"bank|{zhk_name}")],
        [InlineKeyboardButton(text="📊 Презентация", callback_data=f"prez|{zhk_name}")],
        [
            InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_list"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ]
    ])


def get_back_keyboard():
    """Кнопка 'Назад' для поиска"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])


def get_feedback_keyboard():
    """Кнопки для обратной связи"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Написать разработчику", url="tg://user?id=5130067818")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])