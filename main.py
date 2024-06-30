import logging
from bot import TelegramBot
from questions_base import QuestionsBase, Topics

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_token() -> str:
    with open('token', 'r') as f:
        token = f.read()
    return token


def main() -> None:
    # Вставьте сюда свой токен
    questions = QuestionsBase({Topics.GEOGRAPHY: "questions/geography.csv",
                               Topics.TRADITIONS: "questions/traditions.csv",
                               Topics.POLITICS: "questions/politic.csv",
                               Topics.CULTURE: "questions/culture.csv"})
    token = get_token()
    bot = TelegramBot(token, questions)
    bot.run()
    
if __name__ == '__main__':
    main()