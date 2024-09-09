import logging
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from api_requests import get_player_by_tg_id, register_player
from keyboards import change_nickname_keyboard
from states import Registration
from .menu import show_main_menu


async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id

    try:
        player_data = await get_player_by_tg_id(user_id)
        if player_data is not None:
            keyboard = change_nickname_keyboard()
            await message.answer('Ты уже зарегистрирован. Хочешь сменить ник?', reply_markup=keyboard)
        else:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=FSInputFile('public/registration_image.png'),
                caption="🚀 *Давайте начнём регистрацию на сервере Владика!* 🚀\n\nВведите своё имя, чтобы продолжить:",
                parse_mode="Markdown"
            )
            await state.set_state(Registration.WATING_NAME)
    except Exception as e:
        logging.error(f"HTTP request failed: {e}")
        await message.answer("БД недоступна, попробуй позже")


async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text
    try:
        logging.info(f"Attempting to register user {user_id} with name {user_name}")
        await register_player(user_id, user_name)
        logging.info(f"User {user_id} successfully registered")

        logging.info(f"Sending success message to user {user_id}")
        await message.answer(f"Спасибо, {user_name}! Вы успешно зарегистрированы.")

        await show_main_menu(message)

        logging.info(f"Registration process completed for user {user_id}")
    except Exception as e:
        logging.error(f"Error during registration process for user {user_id}: {e}")
        await message.answer("Произошла ошибка при регистрации. Попробуйте снова позже.")
    finally:
        await state.clear()
