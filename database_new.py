from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from loguru import logger

# ВРЕМЕННО: используем жестко заданные ключи для диагностики
# Это отключает использование переменных окружения из config.py
supabase = create_client(
    "https://dabwyonyensfzjwmrsg.supabase.co",  # Твой URL
    "sb_publishable_9ieJuKIUdDVm8yBo_uwMeQ_-LNsQ4kv"   # Твой anon public ключ
)

def get_all_zhk():
    """Возвращает список всех ЖК"""
    try:
        response = supabase.table("uvedomleniya").select("zhk").execute()
        return [row["zhk"] for row in response.data if row.get("zhk")]
    except Exception as e:
        logger.error(f"Ошибка получения списка ЖК: {e}")
        return []

def get_zhk_by_name(name: str):
    """Возвращает данные ЖК по названию"""
    try:
        response = supabase.table("uvedomleniya").select("*").eq("zhk", name).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Ошибка получения данных ЖК '{name}': {e}")
        return None