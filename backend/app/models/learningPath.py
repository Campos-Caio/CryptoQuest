class LearningPath: 
    def __init__(self,userId, name, description, mission_list):
        self.userId = userId
        self.name = name
        self.description = description
        self.mission_list = mission_list
        self.nextMission = mission_list[0] if mission_list else None
        