import asyncio

from aiogram import types

from api_requests import get_player_username
from exceptions.CoordinateNotFoundException import CoordinateNotFoundException
from exceptions.PlayerNotFoundException import PlayerNotFoundException
from exceptions.PlayerOfflineException import PlayerOfflineException
from handlers.mincraft_altar import show_altar_menu
from keyboards import action_menu_keyboard
from minecraft_server import is_player_online, get_all_players, save_last_coordinate
from MinecraftBot import MinecraftBot


async def show_action_menu(message: types.Message):
    keyboard = action_menu_keyboard()
    await message.answer(
        "Выбери действие:",
        reply_markup=keyboard
    )


async def visit_altar(message: types.Message):
    user_id = message.from_user.id
    try:
        bot_instance = MinecraftBot.get_instance()
        if bot_instance is None:
            await message.answer("Сервер еще не запущен. Пожалуйста, запустите сервер сначала.")
            return

        if await is_player_online(user_id):
            players = await get_all_players()
            if 'XUY' in players:
                nickname = await get_player_username(user_id)
                await save_last_coordinate(nickname)
                bot_instance.execute_command("/setblock 0 287 0 minecraft:cobblestone")
                bot_instance.execute_command("/tp XUY 0 288 0")
                bot_instance.execute_command(f"//schem load VladickHouse")
                await asyncio.sleep(1)
                bot_instance.execute_command(f"//paste")
                bot_instance.execute_command("/home")
                bot_instance.execute_command('/gamemode adventure ' + nickname)
                bot_instance.execute_command('/tp ' + nickname + ' XUY')
                await show_altar_menu(message)
            else:
                await message.answer("Что то нет игрока XUY. Без него не получится =(")
        else:
            await message.answer("Ты должен быть в сети")
    except PlayerNotFoundException as e:
        await message.answer("Ты не зарегистрирован")
    except PlayerOfflineException as e:
        await message.answer("Ты не в сети")
    except CoordinateNotFoundException as e:
        await message.answer("Не удалось сохранить координаты")
    except Exception as e:
        await message.answer("Произошла ошибка во время сохранения местоположения")
