import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Загрузка данных
def load_json(name):
    with open(name, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(name, data):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

users = load_json("users.json")
roles = load_json("roles.json")
kazna = load_json("kazna.json")
admins = load_json("admins.json")
bankers = load_json("bankers.json")
laws_uk = load_json("laws_uk.json")
laws_koap = load_json("laws_koap.json")
fines = load_json("fines.json")
logs = load_json("logs.json")

# Проверка администратора
def is_admin(user_id):
    return str(user_id) in admins

# Проверка банкира
def is_banker(user_id):
    return str(user_id) in bankers

# Команда: Помощь
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в Emergency Hamburg RP Help Bot.
Напишите 'Помощь' для списка команд.")

@dp.message()
async def handle_commands(message: Message):
    text = message.text.strip()
    sender_id = str(message.from_user.id)
    username = message.from_user.username or f"id:{sender_id}"

    if text.lower().startswith("казна"):
        await message.answer(f"Баланс казны: {kazna['balance']} eh-coin")
    elif text.lower().startswith("выдатьизказны"):
        if not is_banker(sender_id):
            await message.answer("❌ У вас нет прав банкира.")
            return
        try:
            parts = text.split(maxsplit=3)
            if len(parts) < 4:
                return await message.answer("Использование: ВыдатьИзКазны [user_id/@username] [сумма] [причина]")
            user_str, amount_str, reason = parts[1], parts[2], parts[3]
            amount = int(amount_str)
            if kazna["balance"] < amount:
                return await message.answer("❌ Недостаточно средств в казне.")
            recipient_id = user_str.lstrip("@")
            if recipient_id not in users:
                users[recipient_id] = {"eh-coin": 0}
            users[recipient_id]["eh-coin"] += amount
            kazna["balance"] -= amount
            logs.append({
                "тип": "выдача из казны",
                "банкир": username,
                "получатель": recipient_id,
                "сумма": amount,
                "причина": reason,
                "время": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json("kazna.json", kazna)
            save_json("users.json", users)
            save_json("logs.json", logs)
            await message.answer(f"✅ {amount} eh-coin выдано пользователю {user_str} из казны.")
        except Exception as e:
            await message.answer(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
