import logging

from aiogram import types
from keyboards import main_menu_keyboard, server_menu_keyboard
from api_requests import get_player_by_tg_id
from minecraft_server import is_player_online


async def show_main_menu(message: types.Message):
    user_id = message.from_user.id
    logging.info(f"USER_ID: {user_id}")
    try:
        player_data = await get_player_by_tg_id(user_id)
        if player_data:
            player_name = player_data.get('username', 'Неизвестный')
            player_balance = player_data.get('balance', 0)
            try:
                player_status_boolean = await is_player_online(user_id)
                if player_status_boolean:
                    player_info = f"Ты в сети 🟢\nВаше имя: {player_name}\nВаш баланс: {player_balance}"
                else:
                    player_info = f"Ты не в сети 🔴\nВаше имя: {player_name}\nВаш баланс: {player_balance}"
            except Exception as e:
                logging.error(f"Error checking player online status: {e}")
                player_info = f"Статус неизвестен ⚪\nВаше имя: {player_name}\nВаш баланс: {player_balance}"
        else:
            player_info = "Информация о вас недоступна."
    except Exception as e:
        player_info = "Не удалось получить информацию о пользователе."
        logging.error(f"Failed to get player info: {e}")

    keyboard = main_menu_keyboard()
    await message.answer(
        f"{player_info}",
        reply_markup=keyboard
    )


async def show_server_menu(message: types.Message):
    keyboard = server_menu_keyboard()
    await message.answer(
        "Панель сервера:",
        reply_markup=keyboard
    )


async def handle_back_button(message: types.Message):
    await show_main_menu(message)
