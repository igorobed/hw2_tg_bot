from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiohttp
from states import Form, FormRegister
from utils import is_registered


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if is_registered(message.from_user.id):
        await message.reply("Привет!\nВведите /help для получения списка команд.")
    else:
        # если пользователь не зарегестрирован, то мы запускаем
        # процесс регистрации через FSM
        await message.reply("Как вас зовут?")
        await state.set_state(FormRegister.name)


@router.message(FormRegister.name)
async def cmd_register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Введите ваш вес:")
    await state.set_state(FormRegister.weight)


@router.message(FormRegister.weight)
async def cmd_register_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост:")
    await state.set_state(FormRegister.height)


@router.message(FormRegister.height)
async def cmd_register_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)

    data = await state.get_data()
    name = data.get("name")
    weight = data.get("weight")
    height = data.get("height")
    await message.reply(f"Привет, {name}!\nТвой рост - {height}\nТвой вес - {weight}\nТвой id - {message.from_user.id}")
    await state.clear()


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/form - Пример диалога\n"
        "/keyboard - Пример кнопок\n"
        "/joke - Получить случайную штуку\n"
    )


@router.message(Command("keyboard"))
async def show_keyboard(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Кнопка 1", callback_data="btn1")],
            [InlineKeyboardButton(text="Кнопка 2", callback_data="btn2")],
        ]
    )

    await message.reply("Выберите опцию:", reply_markup=keyboard)


@router.callback_query()
async def handle_callback(callback_query):
    if callback_query.data == "btn1":
        await callback_query.message.reply("Вы нажали Кнопка 1")
    elif callback_query.message.data == "btn2":
        await callback_query.message.reply("Вы нажали Кнопка 2")


# FSM  диалог с пользователем
#@router.message(Command("form"))
#async def start_form(message: Message, state: FSMContext):
#    await message.reply("Как вас зовут?")
#    await state.set_state(Form.name)


#@router.message(Form.name)
#async def process_name(message: Message, state: FSMContext):
#    await state.update_data(name=message.text)
#    await message.reply("Как вас зовут?")
#    await state.set_state(Form.age)


#@router.message(Form.age)
#async def process_age(message: Message, state: FSMContext):
#    data = await state.get_data()
#    name = data.get("name")
#    age = message.text
#    await message.reply(f"Привет, {name}! Тебе {age} лет.")
#    await state.clear()


#@router.message(Command("joke"))
#async def get_joke(message: Message):
#    async with aiohttp.ClientSession() as session:
#        async with session.get("что-то...") as response:
#            joke = await response.json()
#            await message.reply(joke["value"])