class Profile: 
    def __init__(self, avatar, nickname, visualTheme, rewards,
achievements ):
        self.avatar = avatar
        self.nickname = nickname
        self.visualTheme = visualTheme
        self.rewards = rewards
        self.achievements = achievements
    
    def editarPerfil(self,new_nickname, new_avatar, new_visualTheme, new_rewards, new_achievements ):
        self.nickname = new_nickname
        self.avatar = new_avatar
        self.visualTheme = new_visualTheme
        self.rewards = new_rewards
        self.achievements = new_achievements

    
