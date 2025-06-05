class Question:
    def __init__(self, id,statements , options, answer):
        self.id = id
        self.statements = statements
        self.options = options
        self.answer = answer

    def validateAnswer(self, userAnswer):
        return userAnswer == self.answer

