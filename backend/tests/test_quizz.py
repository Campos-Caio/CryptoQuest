import unittest
from backend.app.models.quizz import Quizz

class QuizzTest(unittest.TestCase):
    def setUp(self):
        self.quizz = Quizz(1, 'Quizz 1', 'Quizz 1', 'Resposta 1', 10)

    def test_answer_quizz_correct(self):
        question = "Qual a resposta correta?"
        response = "Resposta 1"
        self.assertEqual(self.quizz.answerQuizz(question, response), 10)

    def test_answer_quizz_incorrect(self):
        question = "Qual a resposta correta?"
        response = "Resposta errada"
        self.assertEqual(self.quizz.answerQuizz(question, response), 0)

if __name__ == '__main__':
    unittest.main()
