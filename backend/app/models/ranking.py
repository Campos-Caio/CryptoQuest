class Ranking: 
    def __init__(self,type):
        self.type = type
        self.userPoints = 0; 
        self.users = []; 

    def generateRanking(self,type):
        self.type = type
        self.userPoints.sort(key=lambda x: x.nivel,reverse=True)
        return self.users
        