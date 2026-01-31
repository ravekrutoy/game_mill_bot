from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import add_user_if_not_exists, get_next_question, get_question, get_user_progress, update_user_progress, get_user_balance, get_user_info, add_to_user_balance, set_user_balance
from keyboards import keyboard_options, main
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


router = Router()

prizes = {
    1: 100,
    2: 200,
    3: 300,
    4: 500,
    5: 1000,
    6: 2000,
    7: 4000,
    8: 8000,
    9: 16000,
    10: 32000,
    11: 64000,
    12: 125000,
    13: 250000,
    14: 500000,
    15: 1000000
}

@router.message(Command('start'))
async def start(message: Message):
    await add_user_if_not_exists(message.from_user.id, message.from_user.username or "unknown")
    await message.answer('Добро пожаловать в игру "Кто хочет стать миллионером?"\n\nНажми кнопку снизу, чтобы начать...',
                             reply_markup=main)
    
async def start_game_for_user(message_or_callback, telegram_id, game_number, question_id):
    await update_user_progress(telegram_id, game_number, question_id)
    question_data = await get_next_question(telegram_id)
    
    if question_data:
        question_text = question_data['question']
        options = question_data['options']
        text = question_text + "\n\n"
        for bukva, option in options.items():
            text += f"{bukva}: {option}\n"

        if isinstance(message_or_callback, Message):
            await message_or_callback.answer(f"🎮 Игра №{game_number}:\n\n" + text, reply_markup=keyboard_options)
        else:
            await message_or_callback.message.answer(f"🎮 Игра №{game_number}:\n\n" + text, reply_markup=keyboard_options)


@router.message(F.text == "Начать Игру №1")
async def start_game(message: Message):
    telegram_id = message.from_user.id
    progress = await get_user_progress(telegram_id)
    if not progress or progress == (0, 0):
        await start_game_for_user(message, telegram_id, 1, 1)
    else:
        game_number, question_id = progress
        question_data = await get_question(game_number, question_id)
        if question_data:
            question_text = question_data['question']
            options = question_data['options']
            text = question_text + "\n\n"
            for bukva, option in options.items():
                text += f"{bukva}: {option}\n"
            await message.answer(f"Ты начал игру №{game_number}.\nВот твой текущий вопрос:\n\n" + text, reply_markup=keyboard_options)
        else:
            await message.answer("Кажется, произошла ошибка с прогрессом. Игра будет начата заново.")
            await start_game_for_user(message, telegram_id, 1, 1)
            



@router.callback_query(F.data.in_({'a', 'b', 'c', 'd'})) 
async def handle_answer(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    progress = await get_user_progress(telegram_id)
    
    if not progress:
        return await callback.message.answer("Сначала начни игру.")  

    game_number, question_id = progress
    question_data = await get_question(game_number, question_id)

    if not question_data:
        return await callback.message.answer("Произошла ошибка при получении вопроса.")

    if question_data['correct'].lower() == callback.data: 
        current_question_number = question_id
        prize = prizes.get(current_question_number, 0)
        await add_to_user_balance(telegram_id, prize)
        await update_user_progress(telegram_id, game_number, question_id + 1)       
        next_question = await get_next_question(telegram_id)  

        if next_question:  
            next_question_number = question_id + 1
            question_text = next_question['question']
            options = next_question['options']
            text = f"❓ Вопрос №{next_question_number}:\n{question_text}\n\n"
            for bukva, option in options.items():
                text += f"{bukva}: {option}\n"

            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                pass

            await callback.message.answer(f"✅ Правильно!\nВаш выйгрышь составляет {prize} сом!\n" + text, reply_markup=keyboard_options)
        else:
            await update_user_progress(telegram_id, game_number + 1, 1)

            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                pass

            kb_next_game = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text=f"Начать Игру №{game_number + 1}")]
            ], resize_keyboard=True, one_time_keyboard=True)

            await callback.message.answer(
                f"✅ Правильно!\n Вы ответили на последний вопрос и получаете 1.000.000 сом!\n"
                f"Все деньги начислены вам на баланс. Чтобы его посмотреть нажмите кнопку /my_info\n\n"
                f"🎉 Ты прошёл все вопросы игры №{game_number}!\n"
                f"👇 Нажми кнопку, чтобы перейти к игре №{game_number + 1}",
                reply_markup=kb_next_game
            )
            await update_user_progress(telegram_id, progress[0] + 1, 1)
    else:
        info = await get_user_info(telegram_id)

        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass

        if info['current_question'] < 10:
            await callback.message.answer("❌ Неправильный ответ. Игра окончена.\n"
                                          "Так как вы не дошли до несгораемой суммы, весь ваш выйгрыш сгорает\n"
                                          "Нажми /start чтобы начать заново.")
            await set_user_balance(telegram_id)
            await update_user_progress(telegram_id, progress[0], 1)
        else:
            await callback.message.answer("❌ Неправильный ответ. Игра окончена.\n"
                                          "Так как вы дошли до несгораемой суммы, вы переходите к следующей игре и ваш выйгрыш начислен вам на баланс\n"
                                          "Чтобы его посмотреть нажмите кнопку /my_info\n"
                                          "Нажми кнопку снизу, чтобы играть дальше.", reply_markup=kb_next_game)
            await update_user_progress(telegram_id, progress[0] + 1, 1)
            



@router.message(Command('my_info'))
async def balance(message: Message):
    telegram_id = message.from_user.id
    info = await get_user_info(telegram_id)
    await message.answer(f"Вам баланс составляет {info['balance']} сом!")

@router.message(Command('top'))
async def balance(message: Message):
    await message.answer(...)


@router.message(Command('rules'))
async def rules(message: Message):
    await message.answer(
            "<b>📜 Правила игры \"Кто хочет стать миллионером?\"</b>\n\n"
            "🎯 Это викторина, в которой тебе предстоит ответить на 15 вопросов с вариантами ответов. "
            "За каждый правильный ответ ты получаешь игровую валюту. Чем дальше — тем сложнее и ценнее вопросы!\n\n"
            "⏳ Ограничений по времени на ответ нет.\n"
            "<b>💡 Важно:</b>\n"
            "Забрать свой выигрыш можно <b>только начиная с 10 вопроса</b>. Если ты остановишься раньше, "
            "игра начнётся сначала, и вопросы могут повторяться.\n"
            "Если ты дойдёшь до <b>10 вопроса</b> и заберёшь выигрыш или полностью пройдёшь игру, "
            "то можешь перейти к <b>игре №2</b> и так далее.\n\n"
            "<b>🔢 Уровни сложности:</b>\n\n"
            "Вопросы делятся на 5 уровней по сложности (по 3 вопроса в каждом):\n"
            "🟢 Уровень 1 (вопросы 1–3) — самые лёгкие\n"
            "🟡 Уровень 2 (вопросы 4–6) — чуть сложнее\n"
            "🟠 Уровень 3 (вопросы 7–9) — средняя сложность\n"
            "🔴 Уровень 4 (вопросы 10–12) — сложные\n"
            "🟣 Уровень 5 (вопросы 13–15) — самые трудные\n\n"
            "Темы могут быть разные, но сложность будет одинаковой в пределах одного уровня.\n\n"
            "<b>💰 Структура выигрыша:</b>\n\n"
            "1.   100 сом.\n"
            "2.   200 сом.\n"
            "3.   300 сом.\n"
            "4.   500 сом.\n"
            "5. 1 000 сом.\n"
            "6. 2 000 сом.\n"
            "7. 4 000 сом.\n"
            "8. 8 000 сом.\n"
            "9. 16 000 сом.\n"
            "10. 32 000 сом. 🔒 Можно забрать выйгрышь\n"
            "11. 64 000 сом.\n"
            "12. 125 000 сом.\n"
            "13. 250 000 сом.\n"
            "14. 500 000 сом.\n"
            "15. 1 000 000 сом. 🏆",
        parse_mode="HTML"
    )
