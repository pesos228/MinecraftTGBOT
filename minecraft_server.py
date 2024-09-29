import asyncio

from mcrcon import MCRcon
import logging
from api_requests import get_player_username, update_player_status, save_location, get_player_by_username, \
    get_player_by_tg_id, get_location, update_player_balance
from config import RCON_HOST, RCON_PASSWORD, RCON_PORT, PORT
import re

from exceptions.CoordinateNotFoundException import CoordinateNotFoundException
from exceptions.PlayerNotFoundException import PlayerNotFoundException
from exceptions.PlayerOfflineException import PlayerOfflineException
from exceptions.ServerUnavailableException import ServerUnavailableException


async def is_port_open(host, port):
    loop = asyncio.get_event_loop()
    conn = loop.create_connection(lambda: asyncio.Protocol(), host, port)
    try:
        await asyncio.wait_for(conn, timeout=0.5)
        return True
    except (asyncio.TimeoutError, OSError):
        return False


async def is_player_online(user_id: int) -> bool:
    if not await is_port_open(RCON_HOST, PORT):
        await update_player_status(user_id, False)
        return False
    try:
        nickname = await get_player_username(user_id)
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command("list")
            players = response.split(":")[1].strip().split(", ")
            if nickname in players:
                await update_player_status(user_id, True)
                return True
            else:
                await update_player_status(user_id, False)
                return False
    except ConnectionRefusedError:
        logging.error(f"Could not connect to Minecraft server. Check if it's running and RCON is enabled.")
    except Exception as e:
        logging.error(f"Error in is_player_online: {e}")

    await update_player_status(user_id, False)
    return False


async def get_all_players():
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
            players = mcr.command("list").strip().split()
            players = players[10:]
            players = [string.replace(",", "") for string in players]
        return players
    except Exception as e:
        logging.error(f"Error fetching player list: {e}")
        return "Не удалось получить список игроков."


async def save_last_coordinate(nickname: str):
    player = await get_player_by_username(nickname)
    if not player:
        raise PlayerNotFoundException(f"Player with nickname {nickname} not found")

    if not await is_player_online(player.get('tgId')):
        raise PlayerOfflineException(f"Player {nickname} is not online")

    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            output = mcr.command(f'execute as {nickname} run data get entity {nickname} Pos')
            match = re.search(r"\[([\d.-]+)d, ([\d.-]+)d, ([\d.-]+)d\]", output)
            if match:
                x = float(match.group(1))
                y = float(match.group(2))
                z = float(match.group(3))
                logging.info(f"{x},{y},{z}")
                await save_location(x, y, z, player.get('tgId'))
            else:
                logging.error("No match found in the output")
                raise CoordinateNotFoundException("No match found in the output")
    except Exception as e:
        logging.error(f"An error occurred while saving the location: {e}")
        raise CoordinateNotFoundException("Не удалось сохранить координаты")


async def return_player_to_last_coordinate(user_id: int):
    player = await get_player_by_tg_id(user_id)
    nickname = player["username"]
    coordinates = await get_location(user_id)
    x = int(coordinates["x"])
    y = int(coordinates["y"])
    z = int(coordinates["z"])
    if not player:
        raise PlayerNotFoundException(f"Player with nickname {nickname} not found")

    if not await is_player_online(user_id):
        raise PlayerOfflineException(f"Player {nickname} is not online")
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            mcr.command(f"tp {nickname} {x} {y} {z}")
            mcr.command(f"gamemode survival {nickname}")
    except Exception as e:
        logging.error(f"Error during player teleportation{e}")
        raise ServerUnavailableException("No match found in the output")


async def get_last_coordinate(user_id: int):
    player = await get_player_by_tg_id(user_id)
    if not player:
        raise PlayerNotFoundException(f"Player with user ID {user_id} not found")

    coordinates = await get_location(user_id)
    x = int(coordinates["x"])
    y = int(coordinates["y"])
    z = int(coordinates["z"])

    return x, y, z


async def gift_to_vladick(result, price, text, item, nickname):
    player = await get_player_by_username(nickname)
    if not player:
        raise PlayerNotFoundException(f"Player with nickname {nickname} not found")
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            num_items = int(re.findall(r"\d+", result)[0])
            balance = player["balance"]
            money = int(num_items * price + int(balance))
            mcr.command('clear ' + nickname + ' ' + item)
            await update_player_balance(money, nickname)
            mcr.command('clear ' + nickname + ' ' + item)
            mcr.command('tellraw ' + nickname + text)
    except Exception as e:
        logging.error(f"Error during player donation{e}")
        raise ServerUnavailableException("No match found in the output")
