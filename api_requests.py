import logging

import aiohttp
from config import ENDPOINT_URL


async def get_player_by_tg_id(user_id: int):
    url = f"{ENDPOINT_URL}/player/tgId/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return None
            else:
                response.raise_for_status()


async def get_player_username(user_id: int):
    player_data = await get_player_by_tg_id(user_id)
    if player_data:
        return player_data.get('username')
    return None


async def get_players():
    url = f"{ENDPOINT_URL}/player"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return None
            else:
                response.raise_for_status()


async def get_player_by_username(username: str):
    url = f"{ENDPOINT_URL}/player/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return None
            else:
                response.raise_for_status()


async def register_player(user_id: int, user_name: str):
    url = f"{ENDPOINT_URL}/player"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"username": user_name, "tgId": user_id}) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()


async def save_location(x: float, y: float, z: float, user_id: int):
    url = f"{ENDPOINT_URL}/location"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"x": x, "y": y, "z": z, "tgId": user_id}) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()


async def get_location(user_id: int):
    url = f"{ENDPOINT_URL}/location/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()


async def update_player(player: dict):
    user_id = player.get('tgId')
    if not user_id:
        raise ValueError("Player data must include 'tgId'")

    url = f"{ENDPOINT_URL}/player"
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=player) as response:
            response_text = await response.text()
            if response.status != 202:
                logging.error(f"Error response: {response_text}")
                response.raise_for_status()


async def update_player_status(user_id: int, status: bool):
    player = await get_player_by_tg_id(user_id)
    if player:
        player['status'] = status
        await update_player(player)
    else:
        raise ValueError(f"Player with ID {user_id} not found.")


async def update_player_username(user_id: int, username: str):
    player = await get_player_by_tg_id(user_id)
    if player:
        player['username'] = username
        await update_player(player)
    else:
        raise ValueError(f"Player with ID {user_id} not found.")


async def update_player_balance(balance: int, username: str):
    player = await get_player_by_username(username)
    if player:
        player['balance'] = balance
        await update_player(player)
    else:
        raise ValueError(f"Player with username {username} not found.")


async def clan_create(user_id: int, clan_name: str):
    url = f"{ENDPOINT_URL}/clan"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"name": clan_name}) as response:
            response.raise_for_status()


async def add_member(user_id: int, clan_name: str, role_name: str):
    async with aiohttp.ClientSession() as session:
        add_member_url = f"{ENDPOINT_URL}/clan/addMember"
        async with session.post(add_member_url,
                                json={"tgId": user_id, "clan_name": clan_name, "role_name": role_name}) as response:
            response.raise_for_status()


async def remove_member(user_id: int, clan_name: str, role_name: str):
    async with aiohttp.ClientSession() as session:
        add_member_url = f"{ENDPOINT_URL}/clan/removeMember"
        async with session.post(add_member_url,
                                json={"tgId": user_id, "clan_name": clan_name, "role_name": role_name}) as response:
            response.raise_for_status()


async def get_clan_by_player_id(user_id: int):
    async with aiohttp.ClientSession() as session:
        get_clan_url = f"{ENDPOINT_URL}/clan/player/{user_id}"
        async with session.get(get_clan_url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def get_all_clans():
    async with aiohttp.ClientSession() as session:
        get_all = f"{ENDPOINT_URL}/clan"
        async with session.get(get_all) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()


async def get_members_clan(name: str):
    async with aiohttp.ClientSession() as session:
        get_all = f"{ENDPOINT_URL}/clan/{name}/members"
        async with session.get(get_all) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def delete_clan(name: str):
    async with aiohttp.ClientSession() as session:
        url = f"{ENDPOINT_URL}/clan"
        async with session.delete(url, json={"name": name}) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
