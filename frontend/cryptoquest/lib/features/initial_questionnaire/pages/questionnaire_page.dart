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

  String _userToken = ''; 

  @override
  void initState() {
    super.initState();

    _userToken =
        'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MWRkZTkzMmViYWNkODhhZmIwMDM3YmZlZDhmNjJiMDdmMDg2NmIiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiQ2FpbyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9jcnlwdG9xdWVzdC05MGE3YiIsImF1ZCI6ImNyeXB0b3F1ZXN0LTkwYTdiIiwiYXV0aF90aW1lIjoxNzUzODkwODQ3LCJ1c2VyX2lkIjoia3Z1WDY2RUlvV09FY2o4QzRTM3dmeUZNVFJLMiIsInN1YiI6Imt2dVg2NkVJb1dPRWNqOEM0UzN3ZnlGTVRSSzIiLCJpYXQiOjE3NTM4OTA4NDgsImV4cCI6MTc1Mzg5NDQ0OCwiZW1haWwiOiJ0ZXN0ZUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsidGVzdGVAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.Ck7dfii5wqqL3VsuUFjuZ5GJbg5iwRPd1bkmCT1wOvZEvHRbst3YlzmANMZzNOeQ3hRRUQBdE-g9G4uuMaXutN-24wui7C5By7suiH1ssfdbEQNUoxCSlj2LzAxHCW5S9b3os-bjaBOBCYPN0956kdploPno9BpF_g0U2yOUlAiQiTkjAA92F89tGPxSnjwJy0V7lFKcr_MWiflEO6GYxBjqexs_Xwlp91_iEj77Flsuh0qFTWpUsAA3UfZEJtWBkOgdIycCuMTXP336paoB_hfB8hqXHQ65vVzTzqwOSbPzYGu2jBkyBXV5cN1bXU16ee30engfqi-MW1gn6KSPCQ';
    // Inicial a busca Pelas perguntas assim que a tela eh construida
    Provider.of<QuestionnaireProvider>(context, listen: false)
        .fetchQuestionnaire(_userToken);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Questionario de Nivelamento!"),
      ),
      body: Consumer<QuestionnaireProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.quesitonnaire == null) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.errorMessage != null) {
            return Center(child: Text("Erro: ${provider.errorMessage}"));
          }

          if (provider.quesitonnaire == null) {
            return const Center(child: Text("Nenhuma pergunta encontrada!"));
          }

          final questions = provider.quesitonnaire!.questions;

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
                  final sucess = await provider.submitAllAnswers(_userToken);

                  if (sucess) {
                    // Navegar para tela principal do app
                    // Navigator.of(context).pushReplacementNamed('/home)
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                        content: Text("Respostas Enviadas com sucesso!")));
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text("Error: ${provider.errorMessage}")));
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
