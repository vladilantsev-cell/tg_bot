from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"KEY: {key[:20]}...")

try:
    supabase = create_client(url, key)
    response = supabase.table("uvedomleniya").select("zhk").execute()
    print("✅ Успешно! Данные:", response.data)
except Exception as e:
    print("❌ Ошибка:", e)