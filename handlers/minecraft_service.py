import asyncio
import logging
import random

from aiogram import types
from aiogram.fsm.context import FSMContext
from mcrcon import MCRcon

import api_requests
from api_requests import get_player_by_tg_id, update_player_balance
from config import RCON_HOST, RCON_PASSWORD
from handlers.minecraft_prank import execute_random_prank
from keyboards import services_menu_keyboard, no_clan_keyboard
from minecraft_server import get_all_players
from states import ClanCreate

prank_lock = asyncio.Lock()


async def show_service_menu(message: types.Message):
    keyboard = services_menu_keyboard()
    await message.answer(
        "Выбери действие:",
        reply_markup=keyboard
    )


async def prank_use(message: types.Message):
    async with prank_lock:
        user_id = message.from_user.id
        player = await get_player_by_tg_id(user_id)
        nickname = player["username"]
        balance = player["balance"]
        if balance >= 100:
            balance = balance - 100
            await update_player_balance(balance, nickname)
            players = await get_all_players()
            players_to_remove = ["XUY", nickname]
            players = [player for player in players if player not in players_to_remove]
            random_index = random.randint(0, len(players) - 1)
            prank_player = players[random_index]
            with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                mcr.command('title @a title "Попался игрок..."')
                await asyncio.sleep(4)
                mcr.command('title @a title {"text":"' + prank_player + '.","color":"red"}')
                mcr.command('playsound minecraft:entity.wither.spawn master @a ~ ~ ~ 10000 1 1')
                await asyncio.sleep(2)
                await execute_random_prank(mcr, prank_player)
        else:
            await message.answer("Недостаточно средств")


async def clan_create(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    player = await get_player_by_tg_id(user_id)
    balance = player["balance"]
    clan = await api_requests.get_clan_by_player_id(user_id)
    if clan is not None:
        await message.answer("У тебя уже есть клан")
        return
    if balance >= 3000:
        await state.update_data(player=player)
        await message.answer("Введите название клана:", reply_markup=no_clan_keyboard())
        await state.set_state(ClanCreate.WAITING_FOR_CLAN_NAME)
    else:
        await message.answer("Недостаточно средств для создания клана")


async def handler_clan_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    clan_name = message.text.strip()
    message_from_user = message.text
    try:
        data = await state.get_data()
        player = data["player"]
        balance = player["balance"] - 3000

        await update_player_balance(balance, player["username"])
        await api_requests.clan_create(user_id, clan_name)
        await api_requests.add_member(user_id, clan_name, "OWNER")

        await message.answer(f"Клан {clan_name} создан!")
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка во время создания клана")
        logging.error(f"There was an error during clan creation: {e}")


async def handle_no_clan(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы отказались от создания клана.", reply_markup=services_menu_keyboard())
