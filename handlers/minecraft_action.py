import asyncio

from aiogram import types

from api_requests import get_player_username, load_vladick_house
from exceptions.CoordinateNotFoundException import CoordinateNotFoundException
from exceptions.PlayerNotFoundException import PlayerNotFoundException
from exceptions.PlayerOfflineException import PlayerOfflineException
from handlers.mincraft_altar import show_altar_menu
from keyboards import action_menu_keyboard
from minecraft_server import is_player_online, get_all_players, save_last_coordinate


async def show_action_menu(message: types.Message):
    keyboard = action_menu_keyboard()
    await message.answer(
        "Выбери действие:",
        reply_markup=keyboard
    )


async def visit_altar(message: types.Message):
    user_id = message.from_user.id
    try:
        if await is_player_online(user_id):
            players = await get_all_players()
            nickname = await get_player_username(user_id)
            await save_last_coordinate(nickname)

            await load_vladick_house(nickname)

            await show_altar_menu(message)
        else:
            await message.answer("Ты должен быть в сети")
    except PlayerNotFoundException as e:
        await message.answer("Ты не зарегистрирован")
    except PlayerOfflineException as e:
        await message.answer("Ты не в сети")
    except CoordinateNotFoundException as e:
        await message.answer("Не удалось сохранить координаты")
    except Exception as e:
        # Логирование ошибки для отладки
        print(f"Unexpected error: {e}")
        await message.answer("Произошла ошибка во время сохранения местоположения")

