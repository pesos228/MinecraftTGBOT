from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    WATING_NAME = State()
    WATING_NEW_NAME = State()


class DuelState(StatesGroup):
    WAITING_PLAYER_SELECTION = State()
    WAITING_BET_AMOUNT = State()
    WAITING_FOR_ACCEPTANCE = State()
    DUEL_STARTED = State()


class ClanCreate(StatesGroup):
    WAITING_FOR_CLAN_NAME = State()


class ClanMemberManagement(StatesGroup):
    SELECTING_MEMBER = State()
    MANAGING_MEMBER = State()


class ClanInviteNewMember(StatesGroup):
    SELECTING_MEMBER = State()
    WAITING_FOR_ACCEPTANCE = State()


class ClanDelete(StatesGroup):
    WAITING_FOR_CHOICE = State()
