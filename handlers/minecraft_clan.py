from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from mcrcon import MCRcon

from api_requests import get_clan_by_player_id, get_all_clans, get_members_clan, get_player_by_tg_id, \
    get_player_by_username, update_player_balance, get_players, add_member, remove_member, delete_clan
from config import RCON_HOST, RCON_PASSWORD
from keyboards import clan_owner_keyboard, clan_member_keyboard, all_clans_keyboard, all_members_of_clan, \
    manage_member_by_owner_keyboard, invite_to_clan_choice, main_menu_keyboard, delete_clan_keyboard
from minecraft_server import is_player_online
from states import ClanMemberManagement, ClanInviteNewMember, ClanDelete


async def show_clan_menu(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    current_clan = await get_clan_by_player_id(user_id)
    if current_clan is not None:
        if current_clan["role_name"] == "OWNER":
            await message.answer("Меню главы клана:", reply_markup=clan_owner_keyboard())
        else:
            await message.answer("Меню клана:", reply_markup=clan_member_keyboard())
    else:
        clans = await get_all_clans()
        await message.answer("Кланы на сервере:", reply_markup=all_clans_keyboard(clans))


async def clan_members(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current_clan = await get_clan_by_player_id(user_id)
    members_json = await get_members_clan(current_clan["clan_name"])
    members = list()
    for member in members_json:
        player = await get_player_by_tg_id(member["tgId"])
        members.append(player["username"])
    keyboard = await all_members_of_clan(members)
    await state.update_data(clan=current_clan, members=members)
    await message.answer("Игроки: ", reply_markup=keyboard)
    await state.set_state(ClanMemberManagement.SELECTING_MEMBER)


async def manage_member(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    member_name = message.text.split()[0]  # Извлекаем имя игрока из текста кнопки
    data = await state.get_data()
    members = data['members']

    if member_name in members:
        member_player = await get_player_by_username(member_name)
        player_info = await get_clan_by_player_id(user_id)
        player_role = player_info['role_name']
        await state.update_data(selected_member=member_player)
        keyboard = await manage_member_by_owner_keyboard(member_player["tgId"], player_role)
        await message.answer(f"Выбранный игрок: {member_name}", reply_markup=keyboard)
        await state.set_state(ClanMemberManagement.MANAGING_MEMBER)
    else:
        await message.answer("Такого игрока нет в списке, выберите другого.")


async def handle_manage_member_actions(message: types.Message, state: FSMContext, bot: Bot):
    action = message.text
    data = await state.get_data()
    selected_member = data['selected_member']
    selected_member_nickname = selected_member['username']
    selected_member_id = selected_member['tgId']
    clan = data['clan']
    clan_name = clan['clan_name']
    user_id = message.from_user.id

    if action == "Исключить из клана":
        await remove_member(clan_name=clan_name, user_id=selected_member['tgId'], role_name='MEMBER')
        await message.answer(f'Вы исключили из клана {selected_member_nickname}')
        await bot.send_message(chat_id=selected_member_id, text=f'Вас исключили из клана {clan_name}. Какая жалость!')
        await show_clan_menu(message, state)
    if action == "Телепортироваться к игроку [100]":
        player = await get_player_by_tg_id(user_id)

        nickname = player["username"]
        player_balance = player["balance"]

        selected_nickname = selected_member["username"]
        if player_balance >= 100:
            if await is_player_online(selected_member["tgId"]):
                with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                    mcr.command(f"tp {nickname} {selected_nickname}")
                player_balance = player_balance - 100
                await update_player_balance(player_balance, nickname)
                await message.answer(f"Вы телепортированы к игроку {selected_nickname}")
            else:
                await message.answer(f"Игрок {selected_nickname} не в сети")
        else:
            await message.answer("Недостаточно средств")

    if action == "Обратно в меню":
        await show_clan_menu(message, state)


async def players_can_invite(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    clan = await get_clan_by_player_id(user_id)
    players = await get_players()
    player_can_invite = list()
    for player in players:
        current_clan = await get_clan_by_player_id(player["tgId"])
        if current_clan is None:
            player_can_invite.append(player["username"])
    if player_can_invite:
        await message.answer("Выберите игрока:", reply_markup=await all_members_of_clan(player_can_invite))
        await state.set_state(ClanInviteNewMember.SELECTING_MEMBER)
        await state.update_data(player_can_invite=player_can_invite, clan=clan, owner_id=user_id)
    else:
        await message.answer("Нет подходящих игроков")


async def handle_invite_player(message: types.Message, state: FSMContext, bot: Bot):
    member_name = message.text.split()[0]
    data = await state.get_data()
    player_can_invite = data['player_can_invite']
    clan = data['clan']
    owner_id = data['owner_id']
    if member_name in player_can_invite:
        selected_player = await get_player_by_username(member_name)
        await message.answer(f'Ты пригласил игрока {member_name}')
        second_user_state = FSMContext(storage=state.storage,
                                       key=StorageKey(bot_id=bot.id, user_id=selected_player["tgId"],
                                                      chat_id=selected_player["tgId"]))
        await second_user_state.update_data(clan=clan, owner_id=owner_id)
        await invite_player(second_user_state, bot, selected_player["tgId"])
        await show_clan_menu(message, state)
    elif member_name == "Обратно":
        await show_clan_menu(message, state)
    else:
        await message.answer("Такого игрока нет в списке, выберите другого")


async def invite_player(state: FSMContext, bot: Bot, user_id: int):
    data = await state.get_data()
    clan = data['clan']
    clan_name = clan['clan_name']
    await bot.send_message(chat_id=user_id, text=f'Тебя пригласили в клан {clan_name}, примешь приглашение?',
                           reply_markup=invite_to_clan_choice())
    await state.set_state(ClanInviteNewMember.WAITING_FOR_ACCEPTANCE)


async def handle_choice_invite_clan(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    clan = data['clan']
    clan_name = clan['clan_name']
    owner_id = data['owner_id']

    user_id = message.from_user.id

    player = await get_player_by_tg_id(user_id)
    player_nickname = player['username']
    if message.text == "Давай":
        await message.answer(f"Теперь вы состоите в клане {clan_name}", reply_markup=main_menu_keyboard())
        await bot.send_message(chat_id=owner_id, text=f'Игрок {player_nickname} принял ваше приглашение в клан')
        await add_member(user_id, clan_name, "MEMBER")
    if message.text == "Я 1000-7":
        await message.answer(f"Вы отказались состоять в клане {clan_name}", reply_markup=main_menu_keyboard())
        await bot.send_message(chat_id=owner_id, text=f'Игрок {player_nickname} отказался от вашего приглашение в клан')


async def leave_clan(message: types.Message):
    user_id = message.from_user.id
    current_clan = await get_clan_by_player_id(user_id)
    clan_name = current_clan['clan_name']
    await remove_member(current_clan['tgId'], clan_name, current_clan['role_name'])
    await message.answer(f'Вы покинули клан {clan_name}', reply_markup=main_menu_keyboard())


async def delete_clan_choice(message: types.Message, state: FSMContext):
    await message.answer('Выбери действие:', reply_markup=delete_clan_keyboard())
    await state.set_state(ClanDelete.WAITING_FOR_CHOICE)


async def handle_delete_choice(message: types.Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    current_clan = await get_clan_by_player_id(user_id)
    if text == "Я уверен":
        await delete_clan(current_clan['clan_name'])
        await message.answer('Ты только что удалил клан, за который заплатит 3000')
        await show_clan_menu(message, state)
    elif text == "Я случайно":
        await message.answer('Вот и правильно')
        await show_clan_menu(message, state)
    else:
        await message.answer('Алё')
