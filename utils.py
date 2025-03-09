import sqlite3
import requests
from mistralai import Mistral
import re
from config import MISTRAL_API_KEY


client = Mistral(api_key=MISTRAL_API_KEY)


def find_calories(text):
    calorie_pattern = r'(\d+)\s*(?:калори[ияй]|ккал|calories?)'
    
    matches = re.findall(calorie_pattern, text, re.IGNORECASE)
    
    if matches:
        calories = [int(match) for match in matches]
        return calories[-1]
    else:
        return None


def get_burned_cal_from_model(in_text):
    chat_response = client.chat.complete(
    model= "mistral-large-latest",
    messages = [
        {
            "role": "user",
            "content": "Ниже будет представлена информация об активности человека и его параметрах. Тебе необходимо сказать, сколько каллорий он сжег в результате данной активности. Ответ должен представлять из себя ТОЛЬКО одно целочисленное значение. Наприер, 543 калорий.\nИнформация о виде активности и параметрах человека: " + in_text,
        },
    ]
    )
    return find_calories(chat_response.choices[0].message.content)


def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None


def create_users_table():
    """Создает таблицу users если она ещё не существует."""
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "weight REAL NOT NULL,"
            "height REAL NOT NULL,"
            "age INTEGER NOT NULL,"
            "city TEXT NOT NULL,"
            "activity INTEGER NOT NULL,"
            "water_goal INTEGER NOT NULL,"
            "calorie_goal INTEGER NOT NULL,"
            "logged_water INTEGER NOT NULL DEFAULT 0,"
            "logged_calories INTEGER NOT NULL DEFAULT 0,"
            "burned_calories INTEGER NOT NULL DEFAULT 0"
            ")"
        )
        connection.commit()


def get_info(user_id):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT water_goal, calorie_goal, logged_water, logged_calories, burned_calories FROM users WHERE id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result


def add_logged_water(user_id, water_add):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET "
            "logged_water = logged_water + ? "
            "WHERE id = ?",
            (water_add, user_id)
        )
        
        connection.commit()


def add_burned(user_id, res_burned):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET "
            "burned_calories = burned_calories + ? "
            "WHERE id = ?",
            (res_burned, user_id)
        )
        
        connection.commit()


def add_logged_calories(user_id, calories_add):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET "
            "logged_calories = logged_calories + ? "
            "WHERE id = ?",
            (calories_add, user_id)
        )
        
        connection.commit()


def add_set_profile(id, name, weight, height, age, city, activity, water_goal, calorie_goal):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET "
            "name = ?, "
            "weight = ?, "
            "height = ?, "
            "age = ?, "
            "city = ?, "
            "activity = ?, "
            "water_goal = ?, "
            "calorie_goal = ? "
            "WHERE id = ?",
            (name, weight, height, age, city, activity, water_goal, calorie_goal, id)
        )
        
        connection.commit()


def clear_logged(user_id):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET "
            "logged_water = ?, "
            "logged_calories = ?, "
            "burned_calories = ? "
            "WHERE id = ?",
            (0, 0, 0, user_id)
        )
        
        connection.commit()


def is_registered(user_id) -> bool:
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE id = ?)",
            (user_id,)
        )
        result = cursor.fetchone()
    return bool(result[0])


def create_user_in_db(id, name, weight, height, age, city, activity, water_goal, calorie_goal):
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, weight, height, age, city, activity, water_goal, calorie_goal) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id, name, weight, height, age, city, activity, water_goal, calorie_goal)
        )
        connection.commit()


def daily_water_norm(weight, activity, temperature=None):
    t_add = 0
    if temperature:
        if temperature > 25:
            t_add = 750
    return weight * 30 + 500 * (activity / 30) + t_add


def daily_calor_norm(weight, height, age, activity=None):
    return 10 * weight + 6.25 * height - 5 * age