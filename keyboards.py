from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from api_requests import get_player_by_username
from minecraft_server import is_player_online


def main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сервер"),
                KeyboardButton(text="Действие")
            ],
            [
                KeyboardButton(text="Услуги"),
                KeyboardButton(text="Кланы")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def change_nickname_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Поменять имя"),
                KeyboardButton(text="Вернуться в главное меню")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def server_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Запустить"),
                KeyboardButton(text="Выключить")
            ],
            [
                KeyboardButton(text="Статус"),
                KeyboardButton(text="Назад")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def action_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Вызвать на дуэль"),
                KeyboardButton(text="Посетить алтарь"),
                KeyboardButton(text="Назад")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def altar_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сделать подношение"),
                KeyboardButton(text="Вернуться назад"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def services_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Пранк [100]"),
                KeyboardButton(text="Создать клан [3000]"),
                KeyboardButton(text="Назад"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def players_menu_keyboard(players):
    buttons = []
    row = []
    for i, player in enumerate(players):
        row.append(KeyboardButton(text=player))
        if (i + 1) % 3 == 0:  # Разбиваем на ряды по 3 кнопки
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([KeyboardButton(text="Я передумал")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите игрока"
    )

    return keyboard


def duel_choice_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Принимаю вызов!⚔"),
                KeyboardButton(text="Да ну нафиг"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню😈"
    )
    return keyboard


def look_duel_choice_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Посмотрю"),
                KeyboardButton(text="Отказываюсь"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню"
    )
    return keyboard


def return_from_duel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Вернуться обратно")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню"
    )
    return keyboard


def no_clan_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Мне не нужен клан")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню"
    )
    return keyboard


def clan_owner_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Объявить войну"),
                KeyboardButton(text="Пригласить"),
            ],
            [
                KeyboardButton(text="Просмотреть участников"),
                KeyboardButton(text="Удалить клан")
            ],
            [
                KeyboardButton(text="Назад"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню"
    )
    return keyboard


def clan_member_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Просмотреть участников"),
                KeyboardButton(text="Выйти из клана"),
            ],
            [
                KeyboardButton(text="Назад"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню"
    )
    return keyboard


def all_clans_keyboard(clans):
    buttons = []
    row = []
    for i, clan in enumerate(clans):
        clan_name = clan['name'] if isinstance(clan, dict) else str(clan)
        row.append(KeyboardButton(text=clan_name))
        if (i + 1) % 3 == 0:  # Разбиваем на ряды по 3 кнопки
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([KeyboardButton(text="Назад")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери клан"
    )

    return keyboard


async def all_members_of_clan(members):
    buttons = []
    row = []
    for i, player in enumerate(members):
        current_player = await get_player_by_username(player)
        if await is_player_online(current_player["tgId"]):
            row.append(KeyboardButton(text=f"{player} 🟢"))
        else:
            row.append(KeyboardButton(text=f"{player} 🔴"))
        if (i + 1) % 3 == 0:  # Разбиваем на ряды по 3 кнопки
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([KeyboardButton(text="Обратно в меню")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите игрока"
    )

    return keyboard


async def manage_member_by_owner_keyboard(user_id: int, player_role: str):
    buttons = []
    if player_role == 'OWNER':
        buttons = [
            [KeyboardButton(text="Исключить из клана")]
        ]

    if await is_player_online(user_id):
        buttons.append([KeyboardButton(text="Телепортироваться к игроку [100]")])

    buttons.append([KeyboardButton(text="Обратно в меню")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard


def invite_to_clan_choice():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Давай"),
                KeyboardButton(text="Я 1000-7"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие из меню"
    )
    return keyboard


def delete_clan_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Я уверен"),
                KeyboardButton(text="Я случайно"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Ты уверен?"
    )
    return keyboard
