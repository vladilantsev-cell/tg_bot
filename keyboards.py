async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data

    try:
        # Главное меню
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