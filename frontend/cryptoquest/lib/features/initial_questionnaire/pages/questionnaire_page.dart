import 'package:cryptoquest/features/initial_questionnaire/models/question_model.dart';
import 'package:cryptoquest/features/initial_questionnaire/state/questionnaire_provider.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class QuestionnairePage extends StatefulWidget {
  const QuestionnairePage({super.key});

  @override
  State<QuestionnairePage> createState() => _QuestionnairePageState();
}

class _QuestionnairePageState extends State<QuestionnairePage> {
  final PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    Provider.of<QuestionnaireProvider>(context, listen: false)
        .fetchQuestionnaire();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Questionario de Nivelamento!"),
      ),
      body: Consumer<QuestionnaireProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.questionnaire == null) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.errorMessage != null) {
            return Center(child: Text("Erro: ${provider.errorMessage}"));
          }

          if (provider.questionnaire == null) {
            return const Center(child: Text("Nenhuma pergunta encontrada!"));
          }

          final questions = provider.questionnaire!.questions;

          return Column(
            children: [
              // Indicator de Progresso
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: LinearProgressIndicator(
                  value: (provider.userAnswers.length) / questions.length,
                ),
              ),
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: questions.length,
                  itemBuilder: (context, index) {
                    final question = questions[index];
                    return _buildQuestionCard(
                        context, question, index, questions.length);
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildQuestionCard(BuildContext context, Question question,
      int currentIndex, int totalQuestions) {
    final provider = Provider.of<QuestionnaireProvider>(context, listen: false);

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            question.text,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(
            height: 24.0,
          ),
          ...question.options.map((option) {
            return Card(
              margin: const EdgeInsets.symmetric(vertical: 8.0),
              child: ListTile(
                title: Text(option.text),
                onTap: () {
                  provider.addAnswer(question.id, option.id);

                  if (currentIndex < totalQuestions - 1) {
                    _pageController.nextPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut);
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                        content: Text(
                            "Questionario finalizado! Clique em enviar!")));
                  }
                },
              ),
            );
          }).toList(),
          const Spacer(),
          if (currentIndex == totalQuestions - 1)
            Center(
              child: ElevatedButton(
                onPressed: () async {
                  final provider = Provider.of<QuestionnaireProvider>(context,
                      listen: false);
                  final sucess = await provider.submitAllAnswers();

                  if (!mounted) return;

                  if (sucess) {
                    // Navegar para tela principal do app
                    Navigator.pushReplacementNamed(context, '/home');
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text(
                            "Error: ${provider.errorMessage ?? 'Ocorreu um erro desconhecido!'} ")));
                  }
                },
                child: provider.isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text("Enviar respostas!"),
              ),
            )
        ],
      ),
    );
  }
}
