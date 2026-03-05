from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Найти по названию", callback_data="find_by_name")],
        [InlineKeyboardButton(text="📋 Показать список ЖК", callback_data="show_list")]
    ])

def get_zhk_list_keyboard(zhk_list):
    """Список ЖК (по 2 в ряд)"""
    buttons = []
    for i in range(0, len(zhk_list), 2):
        row = []
        row.append(InlineKeyboardButton(text=zhk_list[i], callback_data=f"zhk|{zhk_list[i]}"))
        if i + 1 < len(zhk_list):
            row.append(InlineKeyboardButton(text=zhk_list[i+1], callback_data=f"zhk|{zhk_list[i+1]}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_detail_keyboard(zhk_name: str):
    """Клавиатура для конкретного ЖК"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Презентация", callback_data=f"prez|{zhk_name}")],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_list"),
            InlineKeyboardButton(text="🏠 Меню", callback_data="back_to_main")
        ]
    ])

def get_back_keyboard():
    """Кнопка 'Назад' для поиска"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])