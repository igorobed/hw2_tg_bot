from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import aiohttp
from states import FormRegister, FormFoodLog
from utils import *


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if is_registered(message.from_user.id):
        await message.reply("Привет!\nВведите /help для получения списка команд.")
    else:
        await message.reply("Как вас зовут?")
        await state.set_state(FormRegister.name)


@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await message.reply("Как вас зовут?")
    await state.set_state(FormRegister.name)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/help -Показать список комманд\n"
        "/set_profile - Настройка профиля пользователя\n"
        "/log_water <количество в мл> - Логирование воды\n"
        "/log_food <название продукта> - Логирование еды\n"
        "/log_workout <тип тренировки> <время(мин)> - Логирование тренировок\n"
        "/check_progress - Прогресс по воде и калориям\n"
        "/clear_logs - очистить логи прошедшего дня(вода, калории, сожженные калории)"
    )


@router.message(Command("clear_logs"))
async def cmd_clear_logs(message: Message):
    if is_registered(message.from_user.id):
        clear_logged(message.from_user.id)
        await message.reply("накопленные вода, калории и сожженные калории обнулены")
    else:
        await message.reply("Введите /start или /set_profile для регистрации")


@router.message(Command("log_water"))
async def cmd_log_water(message: Message):
    if is_registered(message.from_user.id):
        in_lst = message.text.split(" ")
        if len(in_lst) != 2:
            await message.reply("Сообщение должно соответствовать формату: /log_water <количество в мл>\nПример: /log_water 500")
        else:
            water_count = int(in_lst[1])
            water_goal, calorie_goal, logged_water, logged_calories, burned_cal = get_info(message.from_user.id)
    
            await message.reply(f"Записано {water_count} мл воды")
            add_logged_water(message.from_user.id, water_count)
            logged_water += water_count

            if water_goal >= logged_water:
                await message.reply(f"Выпито {logged_water} мл. До выполнения дневной нормы осталось {water_goal - logged_water} мл воды")
            else:
                await message.reply(f"Выпито {logged_water} мл. Дневная норма превышена на {logged_water - water_goal} мл")
    else:
        await message.reply("Введите /start или /set_profile для регистрации")


@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    if is_registered(message.from_user.id):
        in_lst = message.text.split(" ")
        curr_food = " ".join(in_lst[1:])
        curr_food_info = get_food_info(curr_food)["calories"]
        
        await state.update_data(food_name=curr_food, cal_on_100g=curr_food_info)
    
        await message.reply(f"{curr_food} содержит {curr_food_info} калорий на 100 грамм. Сколько грамм вы съели?")

        await state.set_state(FormFoodLog.food_weight)
    else:
        await message.reply("Введите /start или /set_profile для регистрации")


@router.message(FormFoodLog.food_weight)
async def cmd_register_activity(message: Message, state: FSMContext):
    await state.update_data(food_weight=message.text)
    data = await state.get_data()
    cal_on_100g = int(data.get("cal_on_100g"))
    food_weight = int(data.get("food_weight"))
    add_cal = cal_on_100g * (food_weight / 100.)
    water_goal, calorie_goal, logged_water, logged_calories, burned_cal = get_info(message.from_user.id)
    await message.reply(f"Записано {add_cal} калорий")
    add_logged_calories(message.from_user.id, add_cal)
    await state.clear()


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message):
    if is_registered(message.from_user.id):
        in_lst = message.text.split(" ")
        workout_type = in_lst[1]
        workout_time = int(in_lst[2])
        res_cal = get_burned_cal_from_model(f"{workout_type}  {workout_time} минут")
        #res_cal = 5
        if res_cal is None:
            await message.reply(f"Произошла ошибка в рассчете, попробуйте еще раз")
        else:
            add_burned(message.from_user.id, res_cal)
            await message.reply(f"{workout_type}  {workout_time} минут - {res_cal} ккал")
    else:
        await message.reply("Введите /start или /set_profile для регистрации")


@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    if is_registered(message.from_user.id):
        water_goal, calorie_goal, logged_water, logged_calories, burned_cal = get_info(message.from_user.id)
        await message.reply(
            f"Прогресс:\nВода:\n- Выпито: {logged_water} мл из {water_goal}\n- Осталось: {water_goal - logged_water}\n\nКалории:\n- Потреблено: {logged_calories} ккал из {calorie_goal} ккал\n- Сожжено: {burned_cal} ккал\n- Баланс: {logged_calories - burned_cal}"
            )
    else:
        await message.reply("Введите /start или /set_profile для регистрации")
    

@router.message(FormRegister.name)
async def cmd_register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(FormRegister.weight)


@router.message(FormRegister.weight)
async def cmd_register_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(FormRegister.height)


@router.message(FormRegister.height)
async def cmd_register_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)

    await message.reply("Введить ваш полный возраст в годах:")
    await state.set_state(FormRegister.age)


@router.message(FormRegister.age)
async def cmd_register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(FormRegister.activity)


@router.message(FormRegister.activity)
async def cmd_register_activity(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await message.reply("В каком городе вы находитесь")
    await state.set_state(FormRegister.city)


@router.message(FormRegister.city)
async def cmd_register_weight(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    name = data.get("name")
    weight = data.get("weight")
    height = data.get("height")
    age = data.get("age")
    activity = data.get("activity")
    city = data.get("city")
    daily_water = daily_water_norm(int(weight), int(activity))
    daily_calories = daily_calor_norm(int(weight), int(height), int(age))

    await message.reply(f"Ваша ежедневная норма:\n- Вода: {daily_water}\n- Калории: {daily_calories}")
    if is_registered(message.from_user.id):
        add_set_profile(message.from_user.id, name, weight, height, age, city, activity, daily_water, daily_calories)
    else:
        create_user_in_db(message.from_user.id, name, weight, height, age, city, activity, daily_water, daily_calories)
    await state.clear()


@router.message()
async def handle_unknown_message(message: Message):
    await message.answer("Используйте /help для вывода списка доступных команд.")