from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from os import path
import json
from config import BOT_TOKEN


bot = Bot(BOT_TOKEN)
dp = Dispatcher()

button1 = KeyboardButton(text="/help")
button2 = KeyboardButton(text="/addmeter")
button3 = KeyboardButton(text="/getmymeters")
keyboard = ReplyKeyboardMarkup(keyboard=[[button1], [button2], [button3]], resize_keyboard=True)


def add_user(user_id: int, first_name: str, last_name: str, username: str, lang: str) -> bool:
    users = {}
    file_path = "users.json"
    if path.isfile(file_path):
        with open(file_path, 'r', encoding="UTF-8") as f:
            users = json.load(f)
    if str(user_id) in users.keys():
        return False
    user_info = {"first_name": first_name, "last_name": last_name, "username": username, "lang": lang}
    users[user_id] = user_info
    with open(file_path, 'w', encoding="UTF-8") as f:
        json.dump(users, f)
    return True


def get_meter_data(text: str) -> tuple | bool:
    data = [s.strip() for s in text.replace("/addmeter", "").split(',')]
    if len(data) != 3 or not data[1] in "13" or not data[2].isdigit():
        return False
    name = data[0]
    phases = int(data[1])
    kt = int(data[2])
    is_commerc = False
    return name, phases, kt, is_commerc


def add_meter(name: str, phases: int, kt: int, is_commerc: bool) -> bool:
    data = {}
    file_path = "meters.json"
    if path.isfile(file_path):
        with open(file_path, 'r', encoding="UTF-8") as f:
            data = json.load(f)
    new_id = max([int(i) for i in data]) + 1 if data else 1
    if data and name in [v["name"] for v in data.values()]:
        return False
    else:
        meter = {"name": name, "phases": phases, "kt": kt, "commercial": is_commerc}
        data[new_id] = meter
        with open(file_path, 'w', encoding="UTF-8") as f:
            json.dump(data, f)
        return True


@dp.message(CommandStart())
async def start_command_handler(mess: Message):
    await mess.answer('Привіт!\n Я тестовий бот для обліку електроенергії. Я зараз в розробці.')


@dp.message(Command(commands=['help']))
async def help_command_handler(mess: Message):
    await mess.answer('Тут буде список доступних команд з прикладами використання',
                      reply_markup=ReplyKeyboardRemove())


@dp.message(Command(commands=["addmeter"]))
async def add_meter_handler(mess: Message):
    data = get_meter_data(mess.text)
    if data:
        add_res = add_user(mess.from_user.id, mess.from_user.first_name, mess.from_user.last_name,
                           mess.from_user.username, mess.from_user.language_code)
        greet = f"{mess.from_user.id}, вітаю з початком використання моїх послуг!\n" if add_res else ""
        name, phases, kt, is_commerc = data
        res = add_meter(name, phases, kt, is_commerc)
        if res:
            await mess.answer(f"{greet}Лічильник {name} успішно додано! Переглянути свої лічильники - getmymeters")
        else:
            await mess.answer(f"Лічильник з ім'ям {name} вже існує! Придумайте унікальне ім'я")
    else:
        await mess.answer("Не вдалося додати лічильник! Перевірте формат вводу даних")


@dp.message(Command(commands=["getmymeters"]))
async def get_meters_handler(mess: Message):
    data = {}
    file_path = "meters.json"
    if path.isfile(file_path):
        with open(file_path, 'r', encoding="UTF-8") as f:
            data = json.load(f)
    if data:
        meters = []
        for i, v in enumerate(data.values()):
            s = f"{i+1}. Ім'я: {v['name']}, Фаз: {v['phases']}, Кт: {v['kt']}, Комерційний: {v['commercial']}\n"
            meters.append(s)
        info = "\n".join(meters)
        await mess.answer(info, reply_markup=ReplyKeyboardRemove())
    else:
        await mess.answer("В списку немає лічильників", reply_markup=ReplyKeyboardRemove())


@dp.message()
async def send_answer(mess: Message):
    await mess.reply(text="Наразі текстові повідомлення не можуть бути оброблені",
                     reply_markup=keyboard)


if __name__ == '__main__':
    dp.run_polling(bot)
