import logging
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_token() -> str:
    with open('token', 'r') as f:
        token = f.read()
    return token



# Класс для хранения сессии пользователя
class UserSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.mode = None

# Словарь для хранения сессий пользователей
user_sessions = {}

# Вопросы для режима Практика и Экзамен
practice_questions = [
    ("Практика: Вопрос 1?", ["Ответ 1.1", "Ответ 1.2", "Ответ 1.3"]),
    ("Практика: Вопрос 2?", ["Ответ 2.1", "Ответ 2.2", "Ответ 2.3"]),
]

exam_questions = [
    ("Экзамен: Вопрос 1?", ["Ответ 1.1", "Ответ 1.2", "Ответ 1.3"]),
    ("Экзамен: Вопрос 2?", ["Ответ 2.1", "Ответ 2.2", "Ответ 2.3"]),
]

# Функция для получения следующего вопроса
def get_next_question(mode):
    if mode == "practice":
        question, answers = random.choice(practice_questions)
    else:
        question, answers = random.choice(exam_questions)
    return question, answers

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_sessions[user_id] = UserSession(user_id)

    keyboard = [
        [InlineKeyboardButton("Практика", callback_data='mode_practice')],
        [InlineKeyboardButton("Экзамен", callback_data='mode_exam')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Привет! Выберите режим работы:', reply_markup=reply_markup
    )

# Функция для обработки выбора режима
async def mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    mode = query.data.split('_')[1]
    user_sessions[user_id].mode = mode

    await ask_next_question(update, context, user_id)

# Функция для отправки следующего вопроса
async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id) -> None:
    mode = user_sessions[user_id].mode
    question, answers = get_next_question(mode)

    keyboard = [[InlineKeyboardButton(answer, callback_data=f'answer_{i}')] for i, answer in enumerate(answers)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=user_id, text=question, reply_markup=reply_markup)

# Функция для обработки ответа на вопрос
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    await query.edit_message_text(text=f'Вы выбрали: {query.data.split("_")[1]}')

    # Получаем и отправляем следующий вопрос
    await ask_next_question(update, context, user_id)

def main() -> None:
    # Вставьте сюда свой токен
    token = get_token()
    
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(mode_selection, pattern='mode_'))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern='answer_'))

    application.run_polling()

if __name__ == '__main__':
    main()