class Quiz: 
    def __init__(self,id,title,question,answer,points):
        self.id = id
        self.title = title
        self.question = question
        self.answer = answer
        self.points = points

    def answerQuiz(self, user, answer):
        # Respondendo quiz
        return self.calculatePoints(answer)
    
    def calculatePoints(self, userAnswer):
        # Calculando pontos
        return self.points if userAnswer == self.answer else 0
    
    def showResult(self): 
        # Exibindo resultado

    def updatePoints(self, user, newPoints):
        self.points = newPoints