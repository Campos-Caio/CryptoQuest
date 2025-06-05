import unittest
from backend.app.models.profile import Profile

class TestProfile(unittest.TestCase):
    def setUp(self):
        self.profile = Profile('avatar', 'nickname', 'visualTheme', 'rewards', 'achievements')

    def test_profile_edit(self):
        self.profile.editarPerfil('new_nickname', 'new_avatar', 'new_visualTheme', 'new_rewards', 'new_achievements')
        self.assertEqual(self.profile.nickname, 'new_nickname')
        self.assertEqual(self.profile.avatar, 'new_avatar')
        self.assertEqual(self.profile.visualTheme, 'new_visualTheme')
        self.assertEqual(self.profile.rewards, 'new_rewards')
        self.assertEqual(self.profile.achievements, 'new_achievements')

if __name__ == '__main__':
    unittest.main()
