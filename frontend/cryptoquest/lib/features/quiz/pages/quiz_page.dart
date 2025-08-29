import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/quiz/models/quiz_model.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class QuizPage extends StatefulWidget {
  final String missionId;
  final String quizId;
  final String missionTitle;

  const QuizPage({
    Key? key,
    required this.missionId,
    required this.quizId,
    required this.missionTitle,
  }) : super(key: key);

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  List<int> selectedAnswers = [];
  Quiz? quiz;

  @override
  void initState() {
    super.initState();
    _loadQuiz();
  }

  Future<void> _loadQuiz() async {
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final missionNotifier =
        Provider.of<MissionNotifier>(context, listen: false);

    if (authNotifier.token != null) {
      final loadedQuiz =
          await missionNotifier.loadQuiz(widget.quizId, authNotifier.token!);
      if (loadedQuiz != null) {
        setState(() {
          quiz = loadedQuiz;
          selectedAnswers = List.filled(loadedQuiz.questions.length, -1);
        });
      }
    }
  }

  void _selectAnswer(int questionIndex, int answerIndex) {
    setState(() {
      selectedAnswers[questionIndex] = answerIndex;
    });
  }

  Future<void> _submitQuiz() async {
    if (selectedAnswers.contains(-1)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Responda todas as perguntas!")),
      );
      return;
    }

    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final missionNotifier =
        Provider.of<MissionNotifier>(context, listen: false);

    if (authNotifier.token != null) {
      final success = await missionNotifier.completeMission(
          widget.missionId, selectedAnswers, authNotifier.token!);

      if (success && mounted) {
        // Calcular pontuacao
        int correctAnswers = 0;
        for (int i = 0; i < quiz!.questions.length; i++) {
          if (selectedAnswers[i] == quiz!.questions[i].correctAnswerIndex) {
            correctAnswers++;
          }
        }
        double percentage = (correctAnswers / quiz!.questions.length) * 100;

        _showResultDialog(percentage);
      }
    }
  }

  void _showResultDialog(double percentage) {
    final missionNotifier =
        Provider.of<MissionNotifier>(context, listen: false);
    final result = missionNotifier.lastCompletedMission;

    showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
              title: Text(percentage >= 70 ? 'Parabéns' : 'Tente Novamente!'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Você acertou ${percentage.toStringAsFixed(0)}%'),
                  if (percentage >= 70 && result != null) ...[
                    const SizedBox(
                      height: 8,
                    ),
                    Text('Ganhou ${result['points']} pontos de XP!'),
                    Text('Nivel: ${result['level']} pontos!'),
                  ],
                ],
              ),
              actions: [
                TextButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).pop();
                    },
                    child: const Text("OK"))
              ],
            ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.missionTitle),
        backgroundColor: Colors.deepPurple[700],
      ),
      body: Consumer<MissionNotifier>(
        builder: (context, missionsNotifier, child) {
          if (missionsNotifier.isLoadingQuiz) {
            return const Center(child: CircularProgressIndicator());
          }

          if (missionsNotifier.quizError != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Erro: ${missionsNotifier.quizError}'),
                  const SizedBox(
                    height: 16,
                  ),
                  ElevatedButton(
                    onPressed: _loadQuiz,
                    child: const Text("Tentar Novamente"),
                  ),
                ],
              ),
            );
          }

          if (quiz == null) {
            return const Center(
              child: Text('Quiz não encontrado!'),
            );
          }

          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                Text(
                  quiz!.title,
                  style: Theme.of(context).textTheme.headlineSmall,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(
                  height: 20,
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: quiz!.questions.length,
                    itemBuilder: (context, questionIndex) {
                      final question = quiz!.questions[questionIndex];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 16),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Pergunta ${questionIndex + 1}',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                question.text,
                                style: Theme.of(context).textTheme.bodyLarge,
                              ),
                              const SizedBox(height: 16),
                              ...question.options.asMap().entries.map(
                                    (entry) => RadioListTile<int>(
                                      title: Text(entry.value.text),
                                      value: entry.key,
                                      groupValue:
                                          selectedAnswers[questionIndex],
                                      onChanged: (value) {
                                        _selectAnswer(questionIndex, value!);
                                      },
                                    ),
                                  ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed:
                        missionsNotifier.isSubmitting ? null : _submitQuiz,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple[700],
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: missionsNotifier.isSubmitting
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text(
                            "Enviar respostas",
                            style: TextStyle(color: Colors.white),
                          ),
                  ),
                )
              ],
            ),
          );
        },
      ),
    );
  }
}
