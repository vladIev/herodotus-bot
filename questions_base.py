from __future__ import annotations
import random
from enum import Enum

from question import Question
from topic_loader import TopicLoader

class Topics(Enum):
    GEOGRAPHY=0
    TRADITIONS=1
    POLITICS=2
    CULTURE=3
    EXAM_2023=4
    EXAM_2024_1=5


class QuestionsBase:
    def __init__(self, questions_path):
        self.questions : dict[Topics, list[Question]] = QuestionsBase._load_questions(questions_path)

    def __getitem__(self, topic:Topics)->list[Question]:
        return self.questions[topic]

    @staticmethod
    def _load_questions(questions_path)->dict[Topics, list[Question]]:
        result = {}
        for topic, path in questions_path.items():
            result[topic] = TopicLoader.load(path, topic)
        return result


class QuestionsGenerator:
    def __init__(self, questions):
        self.questions = questions
        self.questions_order = self._shuffle_questions(questions)
        self.question_generators = {topic: self._get_question(topic) for topic in Topics}

    @staticmethod
    def _shuffle_questions(questions_base):
        result = {}
        for topic, questions in questions_base.items():
            order = list(range(len(questions)))
            random.shuffle(order)
            result[topic] = order
        return result
    
    def _get_question(self, topic:Topics):
        for i in self.questions_order[topic]:
            yield self.questions[topic][i]
        
    def get_next_question(self, topic:Topics|None=None)->Question:
        if not self.question_generators:
            return None
        
        tmp_topic = topic
        if tmp_topic is None:
            tmp_topic = random.choice(list(self.question_generators.keys()))

        try:
            return next(self.question_generators[tmp_topic])
        except StopIteration:
            # If all questions have been exhausted for the topic return 
            if topic is None:
                del self.question_generators[tmp_topic]
                return self.get_next_question()

            return None
        
