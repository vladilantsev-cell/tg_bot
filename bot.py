import asyncio
from aiogram import Bot, Dispatcher
from loguru import logger

from config import BOT_TOKEN
from handlers import router

# Настройка логирования
logger.add("bot.log", rotation="1 MB", retention="7 days", level="INFO")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)

async def main():
    logger.info("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен вручную")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")