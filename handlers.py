from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from database import db
import keyboards as kb
from utils import safe_str, format_contacts, format_prezentaciya

router = Router()


class FindZHk(StatesGroup):
    waiting_for_name = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer(
        "👋 Привет! Я бот для просмотра уведомлений по жилым комплексам.\n\n"
        "Выберите действие:",
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
                "🔍 Введите название жилого комплекса:",
                reply_markup=kb.get_back_keyboard()
            )
            await state.set_state(FindZHk.waiting_for_name)

        elif data == "show_list":
            zhk_list = await db.get_all_zhk()
            if not zhk_list:
                await callback.message.edit_text(
                    "😕 Пока нет доступных ЖК.",
                    reply_markup=kb.get_back_keyboard()
                )
            else:
                await callback.message.edit_text(
                    "🏢 Выберите ЖК:",
                    reply_markup=kb.get_zhk_list_keyboard(zhk_list)
                )

        elif data == "back_to_main":
            await state.clear()
            await callback.message.edit_text(
                "👋 Главное меню:",
                reply_markup=kb.get_main_menu_keyboard()
            )

        elif data.startswith("zhk|"):
            _, zhk_name = data.split("|", 1)
            info = await db.get_zhk_by_name(zhk_name)

            if not info:
                await callback.message.edit_text(
                    "❌ ЖК не найден.",
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

        elif data.startswith("prez|"):
            _, zhk_name = data.split("|", 1)
            info = await db.get_zhk_by_name(zhk_name)
            if info and info.get("prezentaciya"):
                await callback.message.answer(
                    format_prezentaciya(info['prezentaciya']),
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            else:
                await callback.message.answer("📭 Презентация не найдена.")

        elif data == "back_to_list":
            zhk_list = await db.get_all_zhk()
            await callback.message.edit_text(
                "🏢 Выберите ЖК:",
                reply_markup=kb.get_zhk_list_keyboard(zhk_list)
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
    info = await db.get_zhk_by_name(zhk_name)

    if not info:
        await message.answer(
            "❌ ЖК с таким названием не найден. Попробуйте ещё раз:",
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


@router.message()
async def ignore_other_messages(message: types.Message):
    """Игнорируем все остальные сообщения"""
    pass