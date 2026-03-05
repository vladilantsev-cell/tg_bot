import os
import sys

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

print("🔍 DEBUG ENV:")
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY length: {len(SUPABASE_KEY) if SUPABASE_KEY else 0}")
print(f"SUPABASE_KEY starts with: {SUPABASE_KEY[:15] if SUPABASE_KEY else 'None'}")
print(f"BOT_TOKEN exists: {'Yes' if BOT_TOKEN else 'No'}")

if not SUPABASE_URL:
    print("❌ SUPABASE_URL missing!")
    sys.exit(1)
if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY missing!")
    sys.exit(1)
if not BOT_TOKEN:
    print("❌ BOT_TOKEN missing!")
    sys.exit(1)

print("✅ Все переменные загружены")