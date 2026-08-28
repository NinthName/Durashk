import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
import os
import random
from dotenv import load_dotenv

# --- НАСТРОЙКИ ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TRIGGER_CHANCE = 0.1

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

# --- ЗАГРУЗКА ТРИГГЕРОВ ---
def load_triggers():
    triggers_file = 'triggers.txt'
    
    if not os.path.exists(triggers_file):
        print(f"⚠️ Файл '{triggers_file}' не найден. Создаю пример...")
        with open(triggers_file, 'w', encoding='utf-8') as f:
            f.write("# Формат: ключевое_слово=url1,url2,url3\n")
            f.write("# Примеры:\n")
            f.write("привет=https://i.postimg.cc/XXXXXX/hello1.jpg,https://i.postimg.cc/YYYYYY/hello2.jpg\n")
            f.write("пока=https://i.postimg.cc/ZZZZZZ/bye.jpg\n")
        print(f"✅ Создан файл '{triggers_file}'. Отредактируйте его и перезапустите бота.")
        return {}
    
    triggers = {}
    try:
        with open(triggers_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                    
                if '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        keyword = parts[0].lower()
                        urls_str = parts[1].strip()
                        urls = [url.strip() for url in urls_str.split(',') if url.strip()]
                        
                        if keyword and urls:
                            triggers[keyword] = urls
                            print(f"✅ Загружен триггер: '{keyword}' → {len(urls)} ссылок")
                        else:
                            print(f"⚠️ Строка {line_num}: пустое слово или нет URL")
                    else:
                        print(f"⚠️ Строка {line_num}: неверный формат")
                else:
                    print(f"⚠️ Строка {line_num}: нет знака '='")
                    
    except Exception as e:
        print(f"❌ Ошибка чтения файла '{triggers_file}': {e}")
        return {}
    
    print(f"📊 Всего загружено слов: {len(triggers)}")
    return triggers

triggers_cache = {}

# --- ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ ---
@router.message(F.text)
async def check_triggers(message: Message):
    global triggers_cache
    
    if not message.text:
        return
    
    if not triggers_cache:
        triggers_cache = load_triggers()
        if not triggers_cache:
            return
    
    text = message.text.lower()
    
    for keyword, urls in triggers_cache.items():
        if keyword in text:
            print(f"🔍 Найдено слово '{keyword}' в сообщении: '{text}'")
            
            if random.random() > TRIGGER_CHANCE:
                print(f"🎲 Шанс не сработал для '{keyword}'")
                return
            
            selected_url = random.choice(urls)
            print(f"🖼 Выбрана ссылка для '{keyword}': {selected_url}")
            
            try:
                await message.reply_photo(photo=selected_url)
                print(f"✅ Отправлено фото для '{keyword}'")
                return
            except Exception as e:
                print(f"❌ Ошибка отправки фото для '{keyword}': {e}")
                try:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=(
                            f"⚠️ <b>Ошибка отправки картинки</b>\n"
                            f"Триггер: <code>{keyword}</code>\n"
                            f"Чат: {message.chat.title or 'Личные сообщения'}\n"
                            f"Ошибка: {e}"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as notify_err:
                    print(f"Не удалось уведомить админа: {notify_err}")
                return

# --- ЗАПУСК БОТА ---
async def main():
    print("🤖 Бот запускается...")
    print(f"🎲 Шанс срабатывания: {int(TRIGGER_CHANCE * 100)}%")
    
    global triggers_cache
    triggers_cache = load_triggers()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")