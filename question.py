class TranslatedStr:
    def __init__(self, original, translated):
        self.original = original
        self.translated = translated

class Question:
    def __init__(self, id:int, topic,  question:TranslatedStr, choices: list[TranslatedStr], correct_answer_index:int):
        self.id = id
        self.topic = topic
        self.question = question
        self.choices = choices
        self.correct_answer = correct_answer_index

    def original(self, prefixes=None):
        if not prefixes:
            prefixes = [''] * len(self.choices)
        choices_str = ''
        for prefix, choice in zip(prefixes, self.choices):
            choices_str += f'{prefix} {choice.original}\n'
        return f'{self.question.original}\n{choices_str}'
    
    def translation(self, prefixes=None):
        if not prefixes:
            prefixes = [''] * len(self.choices)
        choices_str = ''
        for prefix, choice in zip(prefixes, self.choices):
            choices_str += f'{prefix} {choice.translated}\n'
        return f'{self.question.translated}\n{choices_str}'
    
    def answer(self):
        return self.choices[self.correct_answer]
        