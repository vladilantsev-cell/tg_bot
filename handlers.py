import httpx
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from config import SUPABASE_URL, SUPABASE_KEY
import keyboards as kb
from utils import safe_str, format_contacts, format_prezentaciya

router = Router()


class FindZHk(StatesGroup):
    waiting_for_name = State()
    waiting_for_builder = State()


# ===== ПРЯМЫЕ ЗАПРОСЫ К Supabase REST API =====
async def fetch_zhk_list():
    url = f"{SUPABASE_URL}/rest/v1/uvedomleniya"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [item["zhk"] for item in data if item.get("zhk")]
        except Exception as e:
            logger.error(f"Ошибка получения списка ЖК: {e}")
            return []


async def fetch_zhk_by_name(name: str):
    url = f"{SUPABASE_URL}/rest/v1/uvedomleniya"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    params = {
        "zhk": f"eq.{name}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Ошибка получения данных ЖК '{name}': {e}")
            return None


async def fetch_zhk_by_builder(builder: str):
    url = f"{SUPABASE_URL}/rest/v1/uvedomleniya"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    params = {
        "zastroyshchik": f"ilike.*{builder}*"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка поиска по застройщику '{builder}': {e}")
            return []


async def get_stats():
    url = f"{SUPABASE_URL}/rest/v1/uvedomleniya"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            total = len(data)
            builders = len(set(item.get("zastroyshchik") for item in data if item.get("zastroyshchik")))
            return total, builders
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return 0, 0


# ===============================================

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

    welcome_text = (
        "🏢 <b>Добро пожаловать в бота по жилым комплексам!</b>\n\n"
        "Здесь вы можете:\n"
        "🔍 Найти ЖК по названию\n"
        "🏢 Найти ЖК по застройщику\n"
        "📋 Посмотреть список всех ЖК\n"
        "📊 Узнать статистику\n"
        "📧 Связаться с разработчиком\n\n"
        "Выберите действие:"
    )

    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=kb.get_main_menu_keyboard()
    )


@router.message(Command("restart"))
async def cmd_restart(message: types.Message, state: FSMContext):
    await state.clear()
    await cmd_start(message)


@router.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data

    try:
        if data == "find_by_name":
            await callback.message.edit_text(
                "🔍 <b>Поиск по названию</b>\n\nВведите название жилого комплекса:",
                parse_mode="HTML",
                reply_markup=kb.get_back_keyboard()
            )
            await state.set_state(FindZHk.waiting_for_name)

        elif data == "find_by_builder":
            await callback.message.edit_text(
                "🏢 <b>Поиск по застройщику</b>\n\nВведите название застройщика:",
                parse_mode="HTML",
                reply_markup=kb.get_back_keyboard()
            )
            await state.set_state(FindZHk.waiting_for_builder)

        elif data == "show_list":
            zhk_list = await fetch_zhk_list()
            if not zhk_list:
                await callback.message.edit_text(
                    "😕 <b>Пока нет доступных ЖК.</b>",
                    parse_mode="HTML",
                    reply_markup=kb.get_back_keyboard()
                )
            else:
                await callback.message.edit_text(
                    f"🏢 <b>Список ЖК</b> (всего: {len(zhk_list)})\n\nВыберите комплекс:",
                    parse_mode="HTML",
                    reply_markup=kb.get_zhk_list_keyboard(zhk_list, 0)
                )

        elif data.startswith("page|"):
            page = int(data.split("|")[1])
            zhk_list = await fetch_zhk_list()
            await callback.message.edit_text(
                f"🏢 <b>Список ЖК</b> (всего: {len(zhk_list)})",
                parse_mode="HTML",
                reply_markup=kb.get_zhk_list_keyboard(zhk_list, page)
            )

        elif data == "stats":
            total, builders = await get_stats()
            stats_text = (
                f"📊 <b>Статистика базы ЖК</b>\n\n"
                f"🏢 Всего ЖК: <b>{total}</b>\n"
                f"🏗 Застройщиков: <b>{builders}</b>\n"
                f"📅 Последнее обновление: <b>сегодня</b>"
            )
            await callback.message.edit_text(
                stats_text,
                parse_mode="HTML",
                reply_markup=kb.get_back_keyboard()
            )

        elif data == "feedback":
            await callback.message.edit_text(
                "📧 <b>Обратная связь</b>\n\n"
                "По всем вопросам обращайтесь к разработчику:",
                parse_mode="HTML",
                reply_markup=kb.get_feedback_keyboard()
            )

        elif data == "back_to_main":
            await state.clear()
            await callback.message.edit_text(
                "🏠 <b>Главное меню</b>\n\nВыберите действие:",
                parse_mode="HTML",
                reply_markup=kb.get_main_menu_keyboard()
            )

        elif data.startswith("zhk|"):
            _, zhk_name = data.split("|", 1)
            info = await fetch_zhk_by_name(zhk_name)

            if not info:
                await callback.message.edit_text(
                    "❌ <b>ЖК не найден.</b>",
                    parse_mode="HTML",
                    reply_markup=kb.get_back_keyboard()
                )
            else:
                text = (
                    f"🏢 <b>{safe_str(info.get('zhk'))}</b>\n\n"
                    f"🏗 Застройщик: {safe_str(info.get('zastroyshchik'))}\n"
                    f"📄 Уведомление: {safe_str(info.get('uvedomlenie'))}\n"
                    f"💰 Вознаграждение: {safe_str(info.get('voznagrazhdenie'))}\n"
                    f"👤 От кого: {safe_str(info.get('uvedomlenie_kogo'))}\n"
                    f"🏦 Банк: {safe_str(info.get('bank'))}\n\n"
                    f"📞 Контакты:\n{format_contacts(safe_str(info.get('kontakty')))}"
                )
                await callback.message.edit_text(
                    text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=kb.get_detail_keyboard(zhk_name)
                )

        elif data.startswith("contacts|"):
            _, zhk_name = data.split("|", 1)
            info = await fetch_zhk_by_name(zhk_name)
            if info and info.get("kontakty"):
                contacts = format_contacts(info['kontakty'])
                await callback.message.answer(
                    f"📞 <b>Контакты для {safe_str(info.get('zhk'))}:</b>\n\n{contacts}",
                    parse_mode="HTML"
                )
            else:
                await callback.message.answer("📭 Контакты не найдены.")

        elif data.startswith("bank|"):
            _, zhk_name = data.split("|", 1)
            info = await fetch_zhk_by_name(zhk_name)
            if info and info.get("bank"):
                await callback.message.answer(
                    f"🏦 <b>Банк для {safe_str(info.get('zhk'))}:</b>\n\n{info['bank']}",
                    parse_mode="HTML"
                )
            else:
                await callback.message.answer("🏦 Информация о банке не найдена.")

        elif data.startswith("prez|"):
            _, zhk_name = data.split("|", 1)
            info = await fetch_zhk_by_name(zhk_name)
            if info and info.get("prezentaciya"):
                await callback.message.answer(
                    format_prezentaciya(info['prezentaciya']),
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            else:
                await callback.message.answer("📭 Презентация не найдена.")

        elif data == "back_to_list":
            zhk_list = await fetch_zhk_list()
            await callback.message.edit_text(
                f"🏢 <b>Список ЖК</b> (всего: {len(zhk_list)})",
                parse_mode="HTML",
                reply_markup=kb.get_zhk_list_keyboard(zhk_list, 0)
            )

        else:
            await callback.answer("⚠️ Неизвестная команда")

    except Exception as e:
        logger.error(f"Ошибка в callback: {e}")
        await callback.answer("❌ Произошла ошибка")

    await callback.answer()


@router.message(FindZHk.waiting_for_name)
async def find_zhk_by_name(message: types.Message, state: FSMContext):
    zhk_name = message.text.strip()
    info = await fetch_zhk_by_name(zhk_name)

    if not info:
        await message.answer(
            "❌ <b>ЖК с таким названием не найден.</b>\nПопробуйте ещё раз:",
            parse_mode="HTML",
            reply_markup=kb.get_back_keyboard()
        )
        return

    text = (
        f"🏢 <b>{safe_str(info.get('zhk'))}</b>\n\n"
        f"🏗 Застройщик: {safe_str(info.get('zastroyshchik'))}\n"
        f"📄 Уведомление: {safe_str(info.get('uvedomlenie'))}\n"
        f"💰 Вознаграждение: {safe_str(info.get('voznagrazhdenie'))}\n"
        f"👤 От кого: {safe_str(info.get('uvedomlenie_kogo'))}\n"
        f"🏦 Банк: {safe_str(info.get('bank'))}\n\n"
        f"📞 Контакты:\n{format_contacts(safe_str(info.get('kontakty')))}"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=kb.get_detail_keyboard(zhk_name)
    )
    await state.clear()


@router.message(FindZHk.waiting_for_builder)
async def find_zhk_by_builder(message: types.Message, state: FSMContext):
    builder_name = message.text.strip()
    results = await fetch_zhk_by_builder(builder_name)

    if not results:
        await message.answer(
            "❌ <b>ЖК с таким застройщиком не найдены.</b>\nПопробуйте ещё раз:",
            parse_mode="HTML",
            reply_markup=kb.get_back_keyboard()
        )
        return

    text = f"🏢 <b>Найдено ЖК по застройщику '{builder_name}':</b>\n\n"
    for item in results[:5]:
        text += f"• {item.get('zhk')}\n"

    if len(results) > 5:
        text += f"\n...и ещё {len(results) - 5}"

    text += "\n\nЧтобы посмотреть детали, найдите ЖК по названию."

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=kb.get_back_keyboard()
    )
    await state.clear()


# ===== НОВЫЙ ОБРАБОТЧИК НЕИЗВЕСТНЫХ СООБЩЕНИЙ =====
@router.message()
async def handle_unknown(message: types.Message):
    """
    Обрабатывает все неизвестные команды и сообщения
    """
    # Проверяем, не находится ли пользователь в режиме поиска
    state = FSMContext(
        storage=router.message.storage,
        key=(message.chat.id, message.chat.id)
    )
    current_state = await state.get_state()

    if current_state in [FindZHk.waiting_for_name.state, FindZHk.waiting_for_builder.state]:
        # Если пользователь в режиме поиска - игнорируем (обработчики выше уже сработали)
        return

    # Если это неизвестная команда (начинается с /)
    if message.text and message.text.startswith('/'):
        await message.answer(
            "❌ <b>Неизвестная команда</b>\n\n"
            "Воспользуйтесь кнопками в меню или введите /start",
            parse_mode="HTML"
        )
        return

    # Если пользователь просто написал что-то непонятное
    await message.answer(
        "🤷‍♂️ <b>Я вас не понимаю</b>\n\n"
        "Пожалуйста, используйте кнопки в меню или введите /start",
        parse_mode="HTML",
        reply_markup=kb.get_back_keyboard()
    )