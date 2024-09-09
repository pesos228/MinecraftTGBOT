import asyncio
import logging
import subprocess

import psutil
from aiogram import types
from mcrcon import MCRcon
from aiogram import Bot

from MinecraftBot import MinecraftBot
from api_requests import get_players

from config import RCON_HOST, RCON_PASSWORD, PORT
from minecraft_server import get_all_players, is_port_open

server_lock = asyncio.Lock()


async def is_running(process_name, args):
    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            if process.name() == process_name and args in ' '.join(process.cmdline()):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


async def notice_all(bot: Bot, message: str):
    try:
        players = await get_players()
        if players:
            for player in players:
                user_id = player.get('tgId')
                if user_id:
                    try:
                        await bot.send_message(chat_id=user_id, text=message)
                        logging.info(f"Notification sent to user {user_id}")
                    except Exception as e:
                        logging.error(f"Failed to send notification to user {user_id}: {e}")
        else:
            logging.info("No players found to notify.")
    except Exception as e:
        logging.error(f"Failed to fetch players: {e}")


async def start_server(message: types.Message):
    async with server_lock:
        if await is_port_open(RCON_HOST, PORT):
            await message.answer("Сервер уже запускается или запущен.")
        else:
            await message.answer(f"Запуск сервера....")
            try:
                subprocess.Popen(
                    ["C:\\Users\\VlaDick\\Documents\\котлеты\\TGBOT3\\minecraftServer\\start.cmd"],
                    cwd="C:\\Users\\VlaDick\\Documents\\котлеты\\TGBOT3\\minecraftServer")
                await asyncio.sleep(20)
                with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                    MinecraftBot(RCON_HOST, 'XUY', '1.20.4')
                    mcr.command('difficulty hard')
                    await asyncio.sleep(3)
                    mcr.command('gamemode spectator XUY')
                await notice_all(message.bot, f"Сервер запущен!\nIP: 83.102.204.195:{PORT}\nВерсия: 1.20.4")
            except Exception as e:
                logging.error(f"Error on start server {e}")
                await message.answer(f"Не удалось запустить сервер")


async def stop_server(message: types.Message):
    async with server_lock:
        if not await is_port_open(RCON_HOST, PORT):
            await message.answer("Сервер уже выключен.")
            return
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                await message.answer("Выключение сервера...")
                mcr.command('save-all')
                await asyncio.sleep(2)
                mcr.command('stop')
                await message.answer("Сервер выключен.")
        except Exception as e:
            await message.answer("Произошла ошибка во время выключения сервера")


async def status_server(message: types.Message):
    if await is_port_open(RCON_HOST, PORT):
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                players = await get_all_players()
                players = "\n".join(players)
                players = '\n'.join(['-' + line for line in players.splitlines()])
                await message.answer(
                    f"Сервер: в сети 🟢\n" + "Игроки:\n\n" + players + "\n\n" + f"IP: 83.102.204.195:{PORT}\nВерсия: 1.20.4")
        except Exception as e:
            await message.answer("Произошла ошибка во время проверки статуса сервера")
    else:
        await message.answer("Сервер: не в сети 🔴")
