import unittest
from backend.app.models.question import Question


class QuestionTest(unittest.TestCase):
    def setUp(self):
        self.question = Question(1, 'Pergunta 1', ['Alternativa 1', 'Alternativa 2'], 'Alternativa 1')

    def test_verify_correct_answer(self):
        self.assertTrue(self.question.validateAnswer('Alternativa 1'))
        self.assertFalse(self.question.validateAnswer('Alternativa 2'))

if __name__ == '__main__':
    unittest.main()
