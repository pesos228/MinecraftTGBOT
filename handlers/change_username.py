import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from api_requests import update_player_username
from states import Registration
from .menu import show_main_menu


async def change_name_prompt(message: types.Message, state: FSMContext):
    await message.answer("Введите новое имя:")
    await state.set_state(Registration.WATING_NEW_NAME)


async def process_new_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text
    try:
        logging.info(f"Attempting to change name for user {user_id} to {new_name}")
        await update_player_username(user_id, new_name)
        logging.info(f"User {user_id} successfully changed name to {new_name}")

        await message.answer(f"Ваше имя успешно изменено на {new_name}.")

        await show_main_menu(message)

    except Exception as e:
        logging.error(f"Error during name change process for user {user_id}: {e}")
        await message.answer("Произошла ошибка при изменении имени. Попробуйте снова позже.")
    finally:
        await state.clear()
