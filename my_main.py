import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

SESSION_NAME = "test_session"  # любое название

API_ID = os.getenv("API_ID")  # значения из лк телеграма
API_HASH = os.getenv("API_HASH")


async def main():
    # создаем клиент Telegram
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    # полная авторизация (создаст session-файл при первом запуске)
    await client.start()

    # генерируем строку сессии
    session_string = StringSession.save(client.session)

    print("\n" + "=" * 50)
    print("✅ ВАША СТРОКА СЕССИИ:")
    print(session_string)
    print("=" * 50)

    # сохраняем строку в файл и от туда берем ее в секреты
    with open(f"{SESSION_NAME}.txt", "w") as f:
        f.write(session_string)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

    # запускаем как uv run <название файла где находится данная функция>
