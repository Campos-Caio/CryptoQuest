from datetime import date 

class User: 
    def __init__(self,id,name,email,password,register_date,level):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.register_date = register_date
        self.level = level
    
    def viewRank (self): 
        print("Visualizando ranking")

    def answerQuiz(self, quizz, answer): 
        print("Respondendo quiz")
    
    def obterRecomendacoes(self): 
        print("Obtendo recomendações")

    def fazerLogin(self, email, password): 
        return self.email == email and self.password == password
    
    def profileEdit(self, new_name):
        print("Editando perfil")
        self.name = new_name; 

    def acessTrail(self, trail): 
        print("Acessando trail")