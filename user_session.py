import random
from copy import deepcopy
from question import Question
from questions_base import QuestionsGenerator, Topics


class Statistics:
    def __init__(self):
        self.reset()

    def get_stats_row(self):
        return f"""Правильных ответов: {self.correct_answers}/{self.questions_asked}\n\
            Текущий результат: {self.precision()}%"""
    
    def precision(self):
        if self.questions_asked == 0:
            return 100
        return self.correct_answers / self.questions_asked * 100

    def reset(self):
        self.questions_asked = 0
        self.correct_answers = 0
        self.mistakes = {topic:[] for topic in Topics}
    
# Класс для хранения сессии пользователя
class UserSession:
    def __init__(self, user_id:int, questions_generator: QuestionsGenerator):
        self.user_id = user_id
        self.questions_generator = questions_generator
        self.topic:Topics = None
        self.last_question:Question = None
        self.stats = Statistics()

    def update_questions_stats(self, question:Question, is_correct:bool):
        self.stats.questions_asked += 1
        if not is_correct:
            self.stats.mistakes[question.topic].append(question)
        else:
            self.stats.correct_answers += 1

    def work_on_mistakes(self):
        self.questions = self.stats.mistakes
        self.stats.reset()
        self.questions_generator = QuestionsGenerator(self.questions)

    def get_next_question(self, topic=None):
        if not topic:
            topic = self.topic
        question = self.questions_generator.get_next_question(topic)
        if question and len(question.choices) > 2:
            question = self._shuffled_answers(question)
        self.last_question = question
        return question
    
    def has_mistakes(self)->bool:
        return any(self.stats.mistakes.values())
    
    @staticmethod
    def _shuffled_answers(question:Question):
        cpy = deepcopy(question)
        random.shuffle(cpy.choices)
        correct_answer = next((i for i, t in enumerate(cpy.choices) if t.original == question.answer().original), -1)
        cpy.correct_answer = correct_answer
        return cpy
