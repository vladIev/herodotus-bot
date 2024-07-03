from enum import Enum

from user_session import UserSession
from questions_base import Topics, QuestionsBase, QuestionsGenerator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

answers_letters = ['Α)', 'Β)', 'Γ)', 'Δ)', 'Ε)', 'Στ)']
GREEN_CHECK_MARK = "✅"
RED_CROSS_MARK = "❌"

def get_work_on_erros_mesage(session:UserSession):
    return f"""Вы ответили на все доступные в данный момент вопросы!\n
    Статистика: {session.stats.get_stats_row()}\n
    Дальше будут вопросы в которых вы допутсили ошибку
    """

def get_restart_message(session:UserSession):
    f"""Вы ответили на все доступные в данный момент вопросы!\n
    Статистика: {session.stats.get_stats_row()}\n
    Начинаем заново!
    """

class Mode(Enum):
    PRACTICE=0
    EXAM1=1
    EXAM2=2

class TelegramBot:
    def __init__(self, token: str, questions: QuestionsBase):
        self.application = Application.builder().token(token).build()
        self.questions = questions
        self.user_sessions:dict[int, UserSession] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        self.user_sessions[user_id] = UserSession(user_id, QuestionsGenerator(self.questions.questions))

        keyboard = [
            [InlineKeyboardButton("Практика", callback_data=f"mode_{Mode.PRACTICE}")],
            [InlineKeyboardButton("Экзамен 2023", callback_data=f"mode_{Mode.EXAM1}")],
            [InlineKeyboardButton("Экзамен зима 2024", callback_data=f"mode_{Mode.EXAM2}")], 
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            'Этот бот помогает подготовиться к экзамену на знание культуры и истории Кипра.'
            '\nДоступные команды: \n\t/start - сбросить весь прогресс и начать заново'
            '\n\t/stats - просмотр текущей стастистика'
            '\n\t/skip - пропустить текущий ворос и задать новый'
            '\n\nВыберите режим работы:', reply_markup=reply_markup
        )

    async def mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        mode_to_topic = {"Mode.PRACTICE": None, "Mode.EXAM1":Topics.EXAM_2023, "Mode.EXAM2":Topics.EXAM_2024_1}
        user_id = query.from_user.id
        mode = query.data.split('_')[1]
        self.user_sessions[user_id].topic = mode_to_topic[mode]

        await self.ask_next_question(update, context, user_id)


    async def ask_next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id) -> None:
        session = self.user_sessions[user_id]
        question = session.get_next_question()
        if question is None:
            if session.has_mistakes():
                await context.bot.send_message(chat_id=user_id, text=get_work_on_erros_mesage(session))
                session.work_on_mistakes()
                question = session.get_next_question()

        if question is None:
            await context.bot.send_message(chat_id=user_id, text=get_restart_message(session))
            self.user_sessions[user_id] = UserSession(user_id, QuestionsGenerator(self.questions.questions))
            session = self.user_sessions[user_id]
            question = session.get_next_question()

        if question:
            await self.send_question(question, user_id, context)
        else:
            await self.start(update, context)


    async def send_question(self, question, user_id, context):
        letters = answers_letters[0:len(question.choices)]
        keyboard = [[InlineKeyboardButton(letter, callback_data=f'answer_{i}_correct_{question.correct_answer}')] for i, letter in enumerate(letters)]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=user_id, text=question.original(answers_letters), reply_markup=reply_markup)


    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        session = self.user_sessions[user_id]
        _ , answer, _, correct_answer = query.data.split('_')
        is_correct = answer == correct_answer
        session.update_questions_stats(session.last_question, is_correct)

        await self.send_answer_message(query, session, answer, correct_answer, is_correct)

        # Получаем и отправляем следующий вопрос
        await self.ask_next_question(update, context, user_id)

    async def send_answer_message(self, query, session, answer, correct_answer, is_correct):
        if is_correct:
            mark = f"{GREEN_CHECK_MARK}Верно!"
        else:
            mark = f"{RED_CROSS_MARK}Ошибка!"
        
        response = f"""{mark}\n\n{session.last_question.original(answers_letters)}\n{session.last_question.translation(answers_letters)}\nВаш ответ: {answers_letters[int(answer)]}.\nПравильный ответ: {answers_letters[int(correct_answer)]}"""
        await query.edit_message_text(text=response)

    async def user_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
        user_id = update.message.from_user.id
        session = self.user_sessions[user_id]
        await context.bot.send_message(chat_id=user_id, text=f"Ваша текущая статисткика:\n{session.stats.get_stats_row()}")

    async def skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
        user_id = update.message.from_user.id
        await self.ask_next_question(update, context, user_id)


    def run(self) -> None:
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('stats', self.user_stats))
        self.application.add_handler(CommandHandler('skip', self.skip))
        self.application.add_handler(CallbackQueryHandler(self.mode_selection, pattern='mode_'))
        self.application.add_handler(CallbackQueryHandler(self.handle_answer, pattern='answer_'))


        self.application.run_polling()