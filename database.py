from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from loguru import logger

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_zhk():
    """Возвращает список всех ЖК (только названия)"""
    try:
        response = supabase.table("uvedomleniya").select("zhk").execute()
        return [row["zhk"] for row in response.data if row.get("zhk")]
    except Exception as e:
        logger.error(f"Ошибка получения списка ЖК: {e}")
        return []

def get_zhk_by_name(name: str):
    """Возвращает ВСЕ данные по конкретному ЖК (или None)"""
    try:
        response = supabase.table("uvedomleniya").select("*").eq("zhk", name).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Ошибка получения данных ЖК '{name}': {e}")
        return None