from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from loguru import logger
import time
import asyncio


class Database:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.cache = {}
        self.cache_timestamp = 0
        self.CACHE_TTL = 300  # 5 минут
        self.cache_lock = asyncio.Lock()

    async def _load_all_to_cache(self):
        """Загружает ВСЕ данные из таблицы в кэш"""
        async with self.cache_lock:
            try:
                response = self.supabase.table("uvedomleniya").select("*").execute()
                new_cache = {}
                for item in response.data:
                    if item.get('zhk'):
                        new_cache[item['zhk']] = item
                self.cache = new_cache
                self.cache_timestamp = time.time()
                logger.info(f"✅ Кэш обновлён: {len(self.cache)} ЖК")
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки кэша: {e}")

    async def ensure_cache(self):
        """Проверяет, нужно ли обновить кэш"""
        if not self.cache or time.time() - self.cache_timestamp > self.CACHE_TTL:
            await self._load_all_to_cache()

    async def get_all_zhk(self):
        """Возвращает список всех ЖК (из кэша)"""
        await self.ensure_cache()
        return list(self.cache.keys())

    async def get_zhk_by_name(self, name: str):
        """Возвращает данные ЖК (из кэша)"""
        await self.ensure_cache()
        return self.cache.get(name)


# 👇 ЭТА СТРОКА ДОЛЖНА БЫТЬ В КОНЦЕ ФАЙЛА
db = Database()