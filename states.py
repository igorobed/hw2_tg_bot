from aiogram.fsm.state import State, StatesGroup


class FormRegister(StatesGroup):
    name = State()
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()


class FormFoodLog(StatesGroup):
    food_name = State()
    cal_on_100g = State()
    food_weight = State()