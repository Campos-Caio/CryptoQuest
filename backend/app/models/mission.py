class Mission: 
    def __init__(self, id, title, description, type, content, dificulty, reward):
        self.id = id
        self.title = title
        self.description = description
        self.type = type
        self.content = content
        self.dificulty = dificulty
        self.reward = reward
        self.userProgress = None 

    def initMision(self): 
        self.status = 'Em andamento'

    def finishMision(self): 
        self.status = 'Concluído'
    
    def getNextMission(self, previous_mission, user):
        print(" Retorna Próxima missão com base na anterior")
