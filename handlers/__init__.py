from .change_username import change_name_prompt, process_new_name
from .menu import show_server_menu, handle_back_button, show_main_menu
from .mincraft_altar import return_to_last_location, donation
from .minecraft_action import show_action_menu, visit_altar
from .minecraft_clan import show_clan_menu, clan_members, manage_member, handle_manage_member_actions, \
    players_can_invite, handle_invite_player, handle_choice_invite_clan, leave_clan, delete_clan_choice, \
    handle_delete_choice
from .minecraft_duel import duel_menu_keyboard, handle_player_selection, handle_bet_amount, handle_accept_duel, \
    duel_start, back_from_duel, visit_duel, handle_refusal
from .minecraft_panel import start_server, stop_server, status_server
from .minecraft_service import show_service_menu, prank_use, clan_create, handle_no_clan, handler_clan_name
from .registration import cmd_start, process_name
from states import Registration, DuelState, ClanCreate, ClanMemberManagement, ClanInviteNewMember, ClanDelete
from aiogram.filters.command import Command
from aiogram import F

def setup(dp):
    # регистрация/смена пароля
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(change_name_prompt, F.text == "Поменять имя")
    dp.message.register(process_new_name, Registration.WATING_NEW_NAME)
    dp.message.register(process_name, Registration.WATING_NAME)
    dp.message.register(show_main_menu, F.text == "Вернуться в главное меню")
    # главное меню
    dp.message.register(show_server_menu, F.text == "Сервер")
    dp.message.register(show_action_menu, F.text == "Действие")
    dp.message.register(show_service_menu, F.text == "Услуги")
    dp.message.register(show_clan_menu, F.text == "Кланы")
    # действие
    dp.message.register(visit_altar, F.text == "Посетить алтарь")
    dp.message.register(duel_menu_keyboard, F.text == "Вызвать на дуэль")
    # дуэль
    dp.message.register(show_action_menu, F.text == "Отказываюсь")
    dp.message.register(handle_refusal, F.text == "Я передумал")
    dp.message.register(handle_player_selection, DuelState.WAITING_PLAYER_SELECTION)
    dp.message.register(handle_bet_amount, DuelState.WAITING_BET_AMOUNT)
    dp.message.register(handle_accept_duel, F.text == "Да ну нафиг")
    dp.message.register(handle_accept_duel, F.text == "Принимаю вызов!⚔")
    dp.message.register(duel_start, DuelState.DUEL_STARTED)
    dp.message.register(back_from_duel, F.text == "Вернуться обратно")
    dp.message.register(visit_duel, F.text == "Посмотрю")
    #алтарь
    dp.message.register(return_to_last_location, F.text == "Вернуться назад")
    dp.message.register(donation, F.text == "Сделать подношение")
    # услуги
    dp.message.register(prank_use, F.text == "Пранк [100]")
    dp.message.register(clan_create, F.text == "Создать клан [3000]")
    # кланы
    dp.message.register(handler_clan_name, ClanCreate.WAITING_FOR_CLAN_NAME)
    dp.message.register(handle_no_clan, F.text == "Мне не нужен клан")
    dp.message.register(clan_members, F.text == "Просмотреть участников")
    dp.message.register(show_clan_menu, F.text == "Обратно в меню")
    dp.message.register(manage_member, ClanMemberManagement.SELECTING_MEMBER)
    dp.message.register(handle_manage_member_actions, ClanMemberManagement.MANAGING_MEMBER)
    dp.message.register(players_can_invite, F.text == "Пригласить")
    dp.message.register(handle_invite_player, ClanInviteNewMember.SELECTING_MEMBER)
    dp.message.register(handle_choice_invite_clan, ClanInviteNewMember.WAITING_FOR_ACCEPTANCE)
    dp.message.register(leave_clan, F.text == "Выйти из клана")
    dp.message.register(delete_clan_choice, F.text == "Удалить клан")
    dp.message.register(handle_delete_choice, ClanDelete.WAITING_FOR_CHOICE)
    # сервер
    dp.message.register(start_server, F.text == "Запустить")
    dp.message.register(stop_server, F.text == "Выключить")
    dp.message.register(status_server, F.text == "Статус")

    dp.message.register(handle_back_button, F.text == "Назад")
