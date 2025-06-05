class Reward: 
    def __init__(self, id, title,description, type, requirements):
        self.id = id
        self.title = title
        self.description = description
        self.type = type
        self.requirements = requirements
    
    def validateRequirements(self, user):
        return set(self.requirements).issubset(set(user))
    
    def applyReward(self, user):
        print(f"Recompensa {self.title} aplicada ao usuario {user.name}")
        