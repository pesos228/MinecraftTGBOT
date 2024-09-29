import asyncio
import logging
import random
import re

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from mcrcon import MCRcon

from api_requests import get_player_by_tg_id, get_player_by_username, update_player_balance, fight_place
from config import RCON_HOST, RCON_PASSWORD
from keyboards import players_menu_keyboard, duel_choice_keyboard, main_menu_keyboard, action_menu_keyboard, \
    look_duel_choice_keyboard, return_from_duel_keyboard
from minecraft_server import get_all_players, is_player_online, save_last_coordinate, return_player_to_last_coordinate, \
    get_last_coordinate
from states import DuelState

duel_lock = asyncio.Lock()


async def duel_menu_keyboard(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_player_online(user_id):
        player = await get_player_by_tg_id(user_id)
        nickname = player["username"]
        players = await get_all_players()
        players_to_remove = ["XUY", nickname]
        players = [player for player in players if player not in players_to_remove]
        player_registered = list()
        for player in players:
            player_test = await get_player_by_username(player)
            if player_test:
                player_registered.append(player)
        if players:
            keyboard = players_menu_keyboard(player_registered)
            await message.answer("Выберите игрока:", reply_markup=keyboard)
            await state.set_state(DuelState.WAITING_PLAYER_SELECTION)
        else:
            await message.answer("На сервере нет игроков")
    else:
        await message.answer("Ты должен быть в сети")


async def handle_player_selection(message: types.Message, state: FSMContext):
    selected_player_nickname = message.text

    try:
        players = await get_all_players()
        user_id = message.from_user.id
        player = await get_player_by_tg_id(user_id)

        if selected_player_nickname in players:
            await message.answer(
                f"Ты хочешь надрать задницу: {selected_player_nickname}! Введи за сколько ты готов это сделать😈😈:")
            await state.update_data(selected_player_nickname=selected_player_nickname,
                                    player_nickname=player["username"])
            await state.set_state(DuelState.WAITING_BET_AMOUNT)
        else:
            await message.answer("Выберите игрока из списка.")
    except Exception as e:
        logging.error(f"An error occurred while selecting a player for the duel {e}")
        await message.answer("Произошла ошибка. Сервер недоступен")


async def handle_refusal(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы отказались от выбора игрока.", reply_markup=action_menu_keyboard())


async def handle_bet_amount(message: types.Message, state: FSMContext, bot: Bot):
    bet_amount = message.text
    if bet_amount.isdigit():
        try:
            bet_amount = int(bet_amount)
            await state.update_data(bet_amount=bet_amount)
            user_data = await state.get_data()
            selected_player_nickname = user_data.get("selected_player_nickname")
            selected_player = await get_player_by_username(selected_player_nickname)
            selected_player_id = selected_player["tgId"]

            user_id = message.from_user.id
            player = await get_player_by_tg_id(user_id)

            selected_player_balance = selected_player["balance"]
            player_balance = player["balance"]
            if player_balance >= bet_amount and selected_player_balance >= bet_amount:
                if await is_player_online(selected_player["tgId"]) and await is_player_online(user_id):
                    if selected_player:
                        second_user_state = FSMContext(storage=state.storage,
                                                       key=StorageKey(bot_id=bot.id, user_id=selected_player["tgId"],
                                                                      chat_id=selected_player["tgId"]))
                        await second_user_state.update_data(selected_player_nickname=selected_player_nickname,
                                                            player_nickname=player["username"],
                                                            bet_amount=bet_amount)

                        await state.set_state(DuelState.WAITING_FOR_ACCEPTANCE)
                        await send_duel_invitation(player["username"], bet_amount, selected_player["tgId"], message.bot,
                                                   second_user_state)
                        await message.answer(
                            f"Приглашение на дуэль отправлено игроку {selected_player_nickname} со ставкой {bet_amount}.")
                    else:
                        await message.answer("Ошибка: выбранный игрок не найден.")
                        await state.clear()
                else:
                    await message.answer("Игрок не в сети")
                    await state.clear()
            else:
                await message.answer("У тебя или у твоего оппонента недостаточно средств")
        except Exception as e:
            logging.error(f"An error occurred during bid processing {e}")
            await message.answer("Сервер недоступен. Произошла ошибка во время обработки ставки")
    else:
        await message.answer("Укажите правильное число для ставки.")


async def send_duel_invitation(player_username: str, bet_amount: int, user_id: int, bot: Bot,
                               second_user_state: FSMContext):
    await bot.send_message(chat_id=user_id,
                           text=f"Администрация колизея вызывает тебя на бой с: {player_username}⚔\nСтавка: {bet_amount}💵\n\nПримешь ли ты вызов?",
                           reply_markup=duel_choice_keyboard())

    # Установка состояния DuelAcceptanceState для второго пользователя
    await second_user_state.set_state(DuelState.WAITING_FOR_ACCEPTANCE)


async def handle_accept_duel(message: types.Message, state: FSMContext, bot: Bot):
    logging.info(f"handle_accept_duel called for user {message.from_user.id}")
    logging.info(f"Received message: {message.text}")

    user_data = await state.get_data()
    logging.info(f"User data before duel start: {user_data}")

    if not all(key in user_data for key in ["selected_player_nickname", "player_nickname", "bet_amount"]):
        await message.answer("Ошибка: недостаточно данных для начала дуэли.", reply_markup=main_menu_keyboard())
        await state.clear()
        return

    first_user_nickname = user_data["player_nickname"]
    first_user = await get_player_by_username(first_user_nickname)
    first_user_id = first_user["tgId"]
    first_user_state = FSMContext(storage=state.storage,
                                  key=StorageKey(bot_id=bot.id, user_id=first_user_id, chat_id=first_user_id))

    if message.text == "Принимаю вызов!⚔":
        logging.info(f"User {message.from_user.id} accepted the duel")
        await first_user_state.set_state(DuelState.DUEL_STARTED)
        logging.info(f"handle_accept_duel called for user {message.from_user.id}")
        current_state = await state.get_state()
        logging.info(f"Current state for user {message.from_user.id}: {current_state}")

        user_data = await state.get_data()
        logging.info(f"User data before duel start: {user_data}")

        logging.info(f"User {message.from_user.id} accepted the duel")
        await state.clear()
        await duel_start(message, first_user_state, bot)
    elif message.text == "Да ну нафиг":
        logging.info(f"User {message.from_user.id} declined the duel")
        await first_user_state.clear()
        await state.clear()
        await message.answer("Вы отказались от дуэли.", reply_markup=main_menu_keyboard())
        await bot.send_message(chat_id=first_user_id,
                               text=f"Игрок {user_data['selected_player_nickname']} отказался от вашей дуэли.",
                               reply_markup=action_menu_keyboard())
        logging.info(f"User {first_user_id} state cleared")


async def find_winner(player_id: int, selected_player_id: int, player_nickname: str, selected_player_nickname: str,
                      mcr):
    if not await is_player_online(player_id):
        return selected_player_id
    if not await is_player_online(selected_player_id):
        return player_id
    output_player = mcr.command(
        ' execute as ' + str(player_nickname) + ' run data get entity ' + str(player_nickname) + ' Pos')
    match_player = re.search(r"\[([\d.-]+)d, ([\d.-]+)d, ([\d.-]+)d\]", output_player)
    if match_player:
        x = int(float(match_player.group(1)))
        y = int(float(match_player.group(2)))
        z = int(float(match_player.group(3)))
        if x in range(6871, 6921) and y in range(132, 164) and z in range(11961, 12011):
            return selected_player_id

    output_selected_player = mcr.command(' execute as ' + str(selected_player_nickname) + ' run data get entity ' + str(
        selected_player_nickname) + ' Pos')
    match_selected_player = re.search(r"\[([\d.-]+)d, ([\d.-]+)d, ([\d.-]+)d\]", output_selected_player)
    if match_selected_player:
        x = int(float(match_selected_player.group(1)))
        y = int(float(match_selected_player.group(2)))
        z = int(float(match_selected_player.group(3)))
        if x in range(6871, 6921) and y in range(132, 164) and z in range(11961, 12011):
            return player_id


async def send_invitation(player_nickname: str, selected_player_nickname: str, bot):
    players = await get_all_players()
    players_to_remove = ["XUY", player_nickname, selected_player_nickname]
    players = [player for player in players if player not in players_to_remove]
    for player in players:
        player_check = await get_player_by_username(player)
        if player_check is not None and await is_player_online(player_check["tgId"]):
            await bot.send_message(chat_id=player_check["tgId"],
                                   text=f"Администрация колизея приглашает тебя узреть смертную дуэль между ⚔ {player_nickname} и ⚔ {selected_player_nickname}❗ Не пропустите это зрелище!\n\nСогласишься ли на приглашение?🤔",
                                   reply_markup=look_duel_choice_keyboard())
        else:
            logging.warning(f"Player {player} not found or not online")


async def back_from_duel(message: types.Message):
    user_id = message.from_user.id
    await return_player_to_last_coordinate(user_id)
    await message.answer("Выберите действие из меню", reply_markup=main_menu_keyboard())


async def visit_duel(message: types.Message):
    user_id = message.from_user.id
    player = await get_player_by_tg_id(user_id)
    nickname = player["username"]
    await save_last_coordinate(nickname)
    await asyncio.sleep(1)
    with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
        mcr.command(f"tp {nickname} 7987 298 9016")
        await message.answer("Наслаждайся зрелищем!", reply_markup=return_from_duel_keyboard())


async def duel_start(message: types.Message, state: FSMContext, bot: Bot):
    async with duel_lock:
        user_data = await state.get_data()
        selected_player_nickname = user_data.get("selected_player_nickname")
        player_nickname = user_data.get("player_nickname")
        bet_amount = user_data.get("bet_amount")

        logging.info(f"{selected_player_nickname}")
        logging.info(f"{player_nickname}")
        logging.info(f"{bet_amount}")

        if not all(key in user_data for key in ["selected_player_nickname", "player_nickname", "bet_amount"]):
            await message.answer("Ошибка: недостаточно данных для начала дуэли.")
            await state.clear()
            return

        logging.info(f"Starting duel: {player_nickname} vs {selected_player_nickname} with bet {bet_amount}")

        selected_player = await get_player_by_username(selected_player_nickname)
        player = await get_player_by_username(player_nickname)

        selected_player_id = selected_player["tgId"]
        player_id = player["tgId"]

        if await is_player_online(selected_player_id) and await is_player_online(player_id):
            await message.answer(
                f"Вы приняли вызов на дуэль с {player_nickname}! Ставка: {bet_amount}💵\n\nБой начнётся через 15 секунд!",
                reply_markup=main_menu_keyboard())
            await bot.send_message(chat_id=player["tgId"],
                                   text=f"Игрок {selected_player_nickname} принял ваш вызов на дуэль! Ставка: {bet_amount}💵\n\nБой начнётся через 15 секунд!",
                                   reply_markup=main_menu_keyboard())
            await save_last_coordinate(player_nickname)
            await save_last_coordinate(selected_player_nickname)
            await asyncio.sleep(6)

            players = await get_all_players()
            with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                await fight_place(player_nickname, selected_player_nickname)

                tellraw_command = 'tellraw @a {{"text":"[Администрация колизея] ","color":"dark_red","bold":true,"extra":[{{"text":"началась дуэль между ","color":"gold"}},{{"text":"{player_nickname} ","color":"green","bold":true}},{{"text":"и ","color":"gold"}},{{"text":"{selected_player_nickname}","color":"green","bold":true}},{{"text":"! Посетите это зрелище!!","color":"gold"}}]}}'.format(
                    player_nickname=player_nickname, selected_player_nickname=selected_player_nickname)
                mcr.command(tellraw_command)

                await send_invitation(player_nickname, selected_player_nickname, bot)

                await asyncio.sleep(5)

                for nickname in [player_nickname, selected_player_nickname]:
                    mcr.command(f'title {nickname} title "3"')
                    mcr.command(f'playsound minecraft:block.bell.use ambient {nickname} ~ ~ ~ 1000000000 1')
                await asyncio.sleep(1)
                for nickname in [player_nickname, selected_player_nickname]:
                    mcr.command(f'title {nickname} title "2"')
                    mcr.command(f'playsound minecraft:block.bell.use ambient {nickname} ~ ~ ~ 1000000000 0.75')
                await asyncio.sleep(1)
                for nickname in [player_nickname, selected_player_nickname]:
                    mcr.command(f'title {nickname} title "1"')
                    mcr.command(f'playsound minecraft:block.bell.use ambient {nickname} ~ ~ ~ 1000000000 0.5')
                await asyncio.sleep(1)
                mcr.command('fill 8000 288 9004 8000 289 9004 air')
                mcr.command('fill 8000 288 9028 8000 289 9028 air')
                mcr.command(f'spawnpoint {selected_player_nickname} 6900 150 12000')
                mcr.command(f'spawnpoint {player_nickname} 6900 150 12000')
                time = 0
                while time <= 60:
                    await asyncio.sleep(10)
                    winner = await find_winner(player_id, selected_player_id, player_nickname,
                                               selected_player_nickname, mcr)
                    if winner is not None:
                        break
                    time = time + 5
                if winner is not None:
                    if winner == player_id:
                        new_balance = player["balance"] + bet_amount
                        await update_player_balance(new_balance, player_nickname)
                        new_balance = selected_player["balance"] - bet_amount
                        await update_player_balance(new_balance, selected_player_nickname)
                        await bot.send_message(chat_id=player_id,
                                               text=f"🎉 Это была отличная битва! Держи свои заслуженные {bet_amount} 💵. Поздравляем с победой!")
                        await bot.send_message(chat_id=selected_player_id,
                                               text=f"😢 Ты проиграл! Твои {bet_amount} 💵 теперь принадлежат {player_nickname}. Не сдавайся, удача придет в следующий раз!")
                    if winner == selected_player_id:
                        new_balance = selected_player["balance"] + bet_amount
                        await update_player_balance(new_balance, selected_player_nickname)
                        new_balance = player["balance"] - bet_amount
                        await update_player_balance(new_balance, player_nickname)
                        await bot.send_message(chat_id=selected_player_id,
                                               text=f"🎉 Это была отличная битва! Держи свои заслуженные {bet_amount} 💵. Поздравляем с победой!")
                        await bot.send_message(chat_id=player_id,
                                               text=f"😢 Ты проиграл! Твои {bet_amount} 💵 теперь принадлежат {selected_player_nickname}. Не сдавайся, удача придет в следующий раз!")
                else:
                    new_balance = player["balance"] - bet_amount
                    await update_player_balance(new_balance, player_nickname)
                    new_balance = selected_player["balance"] - bet_amount
                    await update_player_balance(new_balance, selected_player_nickname)
                    await bot.send_message(chat_id=player_id,
                                           text=f"😢 Ты проиграл! Твои {bet_amount} 💵 теперь принадлежат администрации колизея. Вы бы ещё чай выпили!")
                    await bot.send_message(chat_id=selected_player_id,
                                           text=f"😢 Ты проиграл! Твои {bet_amount} 💵 теперь принадлежат администрации колизея. Вы бы ещё чай выпили!")

                hint_command_player = 'tellraw {player_name} {{"text":"[Подсказка] ","color":"yellow","bold":true,"extra":[{{"text":"Тебе нужно восстановить свой spawnpoint. Поспи на своей кровати.","color":"white"}}]}}'.format(
                    player_name=player_nickname)
                hint_command_selected_player = 'tellraw {player_name} {{"text":"[Подсказка] ","color":"yellow","bold":true,"extra":[{{"text":"Тебе нужно восстановить свой spawnpoint. Поспи на своей кровати.","color":"white"}}]}}'.format(
                    player_name=selected_player_nickname)

                mcr.command(hint_command_player)
                mcr.command(hint_command_selected_player)

                last_location_player = await get_last_coordinate(player_id)
                last_location_selected_player = await get_last_coordinate(selected_player_id)

                logging.info(f"Last location for {player_nickname}: {last_location_player}")
                logging.info(f"Last location for {selected_player_nickname}: {last_location_selected_player}")

                await return_player_to_last_coordinate(player_id)
                await return_player_to_last_coordinate(selected_player_id)

                await asyncio.sleep(1)

                mcr.command(
                    f'spawnpoint {player_nickname} {last_location_player[0]} {last_location_player[1]} {last_location_player[2]}')
                mcr.command(
                    f'spawnpoint {selected_player_nickname} {last_location_selected_player[0]} {last_location_selected_player[1]} {last_location_selected_player[2]}')

                logging.info(
                    f'spawnpoint {player_nickname} {last_location_player[0]} {last_location_player[1]} {last_location_player[2]}')
                logging.info(
                    f'spawnpoint {selected_player_nickname} {last_location_selected_player[0]} {last_location_selected_player[1]} {last_location_selected_player[2]}')

                await state.clear()

        else:
            await message.answer("Ты или твой оппонент не в сети.")
