import aiosqlite

DB_NAME = "quiz_game.db"
async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT 0,
        current_game INTEGER DEFAULT 1,
        current_question INTEGER DEFAULT 1
        )
        ''')

        await db.execute('''
        CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_number INTEGER,
        level INTEGER,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_option TEXT
        )
        ''')

        await db.commit()

async def add_user_if_not_exists(telegram_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        user = await db.execute('''
        SELECT * FROM users WHERE telegram_id = ?
        ''', (telegram_id,))
        result = await user.fetchone()

        if result is None:
            await db.execute('''
                INSERT INTO users (telegram_id, username)
                VALUES (?, ?)
            ''', (telegram_id, username))
            await db.commit()
            
async def get_question(game_number: int, id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(''' 
            SELECT question, option_a, option_b, option_c, option_d, correct_option
            FROM questions 
            WHERE game_number = ? AND id = ? 
        ''', (game_number, id))

        question_data = await cursor.fetchone()

        if question_data:
            return {
                'question': question_data[0],
                'options': {
                    'A': question_data[1],
                    'B': question_data[2],
                    'C': question_data[3],
                    'D': question_data[4],
                },
                'correct': question_data[5]  
            }
        return None

async def get_user_progress(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT current_game, current_question
            FROM users
            WHERE telegram_id = ?       
        ''', (telegram_id,))
        
        progress = await cursor.fetchone()
        
        return progress

async def update_user_progress(telegram_id: int, current_game: int, current_question: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(''' 
            UPDATE users
            SET current_game = ?, current_question = ?
            WHERE telegram_id = ?       
        ''', (current_game, current_question, telegram_id))
        
        await db.commit()


async def get_next_question(telegram_id: int):
    progress = await get_user_progress(telegram_id)
    if progress:
        current_game, current_question = progress
        question_data = await get_question(game_number=current_game, id = current_question)
        return question_data
    
async def get_user_balance(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
        SELECT balance 
        FROM users 
        WHERE telegram_id = ?                 
        ''', (telegram_id,))
        
        balance = await cursor.fetchone()
        
        if balance: 
            return balance[0]
        else:
            return None
        
async def get_user_info(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT balance, current_game, current_question
            FROM users 
            WHERE telegram_id = ?
        ''', (telegram_id,))
        
        user_info = await cursor.fetchone()
        
        if user_info:
            return {
                'balance': user_info[0],
                'current_game': user_info[1],
                'current_question': user_info[2]
            }
        else:
            return None 
    
async def add_to_user_balance(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users
            SET balance = ?
            WHERE telegram_id = ?
        ''', (amount, telegram_id))
        await db.commit()

        
async def set_user_balance(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users
            SET balance = 0
            WHERE telegram_id = ?
        ''', (telegram_id,))
        await db.commit()




















# async def add_question_to_db(game_number: int, level: int, question: str,
#                              option_a: str, option_b: str,
#                              option_c: str, option_d: str,
#                              correct_option: str):
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute('''
#             INSERT INTO questions (game_number, level, question, option_a, option_b, option_c, option_d, correct_option)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (game_number, level, question, option_a, option_b, option_c, option_d, correct_option))
#         await db.commit()

# async def add_all_questions():
#     questions = [
#         (2, 1, "Сколько пальцев на одной руке у человека?", "4", "5", "6", "10", "B"),
#         (2, 1, "Какой напиток получается из зёрен кофе?", "Чай", "Кофе", "Сок", "Лимонад", "B"),
#         (2, 1, "Кто говорит 'мяу'?", "Собака", "Лошадь", "Кошка", "Корова", "C"),
#
#         # Уровень 2
#         (2, 2, "Кто написал сказку 'Золотой ключик, или Приключения Буратино'?", "Корней Чуковский", "Александр Волков",
#          "Алексей Толстой", "Николай Носов", "C"),
#         (2, 2, "Как называется учение о растениях?", "Зоология", "Геология", "Астрономия", "Ботаника", "D"),
#         (2, 2, "Какой цвет флага России находится сверху?", "Синий", "Белый", "Красный", "Зелёный", "B"),
#
#         # Уровень 3
#         (2, 3, "Как называется самая длинная река в мире?", "Амазонка", "Нил", "Янцзы", "Миссисипи", "A"),
#         (2, 3, "В какой стране находится город Стамбул?", "Греция", "Турция", "Египет", "Италия", "B"),
#         (2, 3, "Что изучает астрономия?", "Земные недра", "Древние культуры", "Звёзды и планеты", "Растения", "C"),
#
#         # Уровень 4
#         (2, 4, "Кто является автором картины 'Тайная вечеря'?", "Микеланджело", "Рафаэль", "Леонардо да Винчи", "Ван Гог",
#          "C"),
#         (2, 4, "Как называется единица измерения силы тока?", "Ом", "Вольт", "Ампер", "Ватт", "C"),
#         (2, 4, "В каком году человек впервые ступил на Луну?", "1959", "1969", "1975", "1981", "B"),
#
#         # Уровень 5
#         (2, 5, "Какой орган у человека отвечает за фильтрацию крови?", "Печень", "Лёгкие", "Почки", "Селезёнка", "C"),
#         (2, 5, "Кто написал роман 'Мастер и Маргарита'?", "Булгаков", "Достоевский", "Тургенев", "Чехов", "A"),
#         (2, 5, "Какой элемент обозначается символом 'Au' в таблице Менделеева?", "Серебро", "Золото", "Уран", "Алюминий",
#          "B"),
#     ]
#
#     for q in questions:
#         await add_question_to_db(*q)



