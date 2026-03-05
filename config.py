import os
import sys

# Переменные окружения (на Render они задаются в панели)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Проверка наличия переменных
if not SUPABASE_URL:
    print("❌ SUPABASE_URL is missing!")
    sys.exit(1)
if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY is missing!")
    sys.exit(1)
if not BOT_TOKEN:
    print("❌ BOT_TOKEN is missing!")
    sys.exit(1)

print("✅ Все переменные окружения загружены")