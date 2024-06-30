import csv
from question import TranslatedStr, Question

class TopicLoader:
    @staticmethod
    def load(path, topic)->list[Question]:
        with open(path, newline='', encoding="utf8") as csvfile:
           questions = TopicLoader._parseCsv(csvfile, topic)

        return questions

    @staticmethod
    def _parseCsv(file, topic)->list[Question]:
        reader = csv.reader(file, delimiter='|', quotechar='"')
        _ = next(reader)
        questions = []
        for row in reader:
            question = TopicLoader._buildQuestion(row, topic)
            if question:
                questions.append(question)
        
        return questions

    @staticmethod
    def _buildQuestion(row:str, topic)->Question:
        if len(row) > 5:
            print(f"\nParsing error: {row}")
        id = row[0]
        question_text = row[1]
        choices_orgn = TopicLoader._splitChoices(row[2], ['Α)', 'Β)', 'Γ)', 'Δ)', 'Ε)', 'Στ)', 'α)', 'β)', 'γ)', 'δ)'])
        if len(choices_orgn) > 4 or len(choices_orgn) == 1:
            print(f"\nWarning to many choices for question:{id}. Choices: {choices_orgn}")
        answer = int(row[3])
        translation_text, translation_choices = TopicLoader._get_translation(row[4], ['А)', 'В)', 'Г)', 'Д)', 'Е)', 'С)'])
        if len(choices_orgn) != len(translation_choices):
            print(f"\nFailed to load translation for: {id} {question_text}. Choices: {choices_orgn}, Translated choices: {translation_choices}")
            return None
        choices = [TranslatedStr(org, trnsl) for org, trnsl in zip(choices_orgn, translation_choices)]
        return Question(id, topic, TranslatedStr(question_text, translation_text), choices, answer)

    @staticmethod
    def _splitChoices(row:str, letters)->list[str]:
        choices = []
        last_pos = 0
        for letter in letters:
            pos = row.find(letter, last_pos) 
            if pos > 0:
                choices.append(row[(last_pos+3):pos- len(letter)])
                last_pos = pos
            
        choices.append(row[last_pos+3:])
        return choices
    
    @staticmethod
    def _get_translation(row:str, letters:list[str]):
        sep = row.find(letters[0])
        question_text = row[:sep]
        choices_text = row[sep:]
        choices = TopicLoader._splitChoices(choices_text, letters)
        return question_text, choices
                
#geograpy_questions = TopicLoader.load("questions/geography.csv")
#traditions_questions = TopicLoader.load("questions/traditions.csv")
#politic_questions = TopicLoader.load("questions/politic.csv")
#culture_questions = TopicLoader.load("questions/culture.csv")

