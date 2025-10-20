import 'package:cryptoquest/features/initial_questionnaire/models/question_model.dart';
import 'package:cryptoquest/features/initial_questionnaire/state/questionnaire_provider.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
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
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text(
          "Questionário de Nivelamento",
          style: TextStyle(
            color: AppColors.onSurface,
            fontWeight: FontWeight.bold,
          ),
        ),
        iconTheme: const IconThemeData(color: AppColors.accent),
      ),
      body: Consumer<QuestionnaireProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.questionnaire == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: AppColors.accent),
                  const SizedBox(height: 16),
                  Text(
                    "Carregando questionário...",
                    style: TextStyle(color: AppColors.onSurfaceVariant),
                  ),
                ],
              ),
            );
          }

          if (provider.errorMessage != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, color: AppColors.error, size: 64),
                  const SizedBox(height: 16),
                  Text(
                    "Erro: ${provider.errorMessage}",
                    style: TextStyle(color: AppColors.error),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            );
          }

          if (provider.questionnaire == null) {
            return Center(
              child: Text(
                "Nenhuma pergunta encontrada!",
                style: TextStyle(color: AppColors.onSurfaceVariant),
              ),
            );
          }

          final questions = provider.questionnaire!.questions;

          return Column(
            children: [
              // Header com título e progresso
              Container(
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  border: Border(
                    bottom: BorderSide(color: AppColors.cardBorder, width: 1),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.psychology,
                            color: AppColors.accent, size: 24),
                        const SizedBox(width: 12),
                        Text(
                          "Vamos conhecer você!",
                          style: TextStyle(
                            color: AppColors.onSurface,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: LinearProgressIndicator(
                              value: (provider.userAnswers.length) /
                                  questions.length,
                              backgroundColor: AppColors.surfaceVariant,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                  AppColors.accent),
                              minHeight: 8,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          "${provider.userAnswers.length}/${questions.length}",
                          style: TextStyle(
                            color: AppColors.accent,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Perguntas
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: questions.length,
                  itemBuilder: (context, index) {
                    final question = questions[index];
                    return _buildQuestionCard(
                        context, question, index, questions.length, provider);
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildQuestionCard(
    BuildContext context,
    Question question,
    int currentIndex,
    int totalQuestions,
    QuestionnaireProvider provider,
  ) {
    // Verificar qual opção está selecionada
    final selectedAnswer = provider.userAnswers
        .firstWhere(
          (answer) => answer.questionId == question.id,
          orElse: () => UserAnswer(questionId: '', selectedOptionId: ''),
        )
        .selectedOptionId;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Número da pergunta
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.accent.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.accent, width: 1),
            ),
            child: Text(
              "Pergunta ${currentIndex + 1} de $totalQuestions",
              style: TextStyle(
                color: AppColors.accent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Pergunta
          Text(
            question.text,
            style: TextStyle(
              color: AppColors.onSurface,
              fontSize: 20,
              fontWeight: FontWeight.bold,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 24),

          // Opções
          ...question.options.asMap().entries.map((entry) {
            final index = entry.key;
            final option = entry.value;
            final isSelected = selectedAnswer == option.id;
            final optionLetters = ['A', 'B', 'C', 'D'];

            return _buildOptionCard(
              context: context,
              optionLetter: optionLetters[index],
              optionText: option.text,
              isSelected: isSelected,
              onTap: () async {
                provider.addAnswer(question.id, option.id);

                // Pequeno delay para mostrar seleção antes de avançar
                await Future.delayed(const Duration(milliseconds: 300));

                if (currentIndex < totalQuestions - 1) {
                  // Não é a última pergunta, apenas avançar
                  _pageController.nextPage(
                    duration: const Duration(milliseconds: 400),
                    curve: Curves.easeInOut,
                  );
                } else {
                  // É a última pergunta, enviar automaticamente
                  if (!mounted) return;

                  final success = await provider.submitAllAnswers();

                  if (!mounted) return;

                  if (success) {
                    // Mostrar feedback de sucesso antes de navegar
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Row(
                          children: [
                            Icon(Icons.check_circle, color: AppColors.success),
                            const SizedBox(width: 12),
                            const Text('Respostas enviadas com sucesso!'),
                          ],
                        ),
                        backgroundColor: AppColors.surface,
                        duration: const Duration(milliseconds: 1500),
                      ),
                    );

                    // Aguardar um pouco antes de navegar
                    await Future.delayed(const Duration(milliseconds: 800));

                    if (!mounted) return;
                    Navigator.pushReplacementNamed(context, '/home');
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Row(
                          children: [
                            Icon(Icons.error_outline, color: AppColors.error),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                provider.errorMessage ??
                                    'Erro ao enviar respostas!',
                              ),
                            ),
                          ],
                        ),
                        backgroundColor: AppColors.surface,
                        action: SnackBarAction(
                          label: 'Tentar novamente',
                          textColor: AppColors.accent,
                          onPressed: () async {
                            final retry = await provider.submitAllAnswers();
                            if (retry && mounted) {
                              Navigator.pushReplacementNamed(context, '/home');
                            }
                          },
                        ),
                      ),
                    );
                  }
                }
              },
            );
          }).toList(),

          const SizedBox(height: 24),

          // Botão de navegação (apenas Voltar)
          if (currentIndex > 0)
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  _pageController.previousPage(
                    duration: const Duration(milliseconds: 300),
                    curve: Curves.easeInOut,
                  );
                },
                icon: Icon(Icons.arrow_back,
                    color: AppColors.onSurfaceVariant, size: 18),
                label: Text(
                  "Voltar",
                  style: TextStyle(color: AppColors.onSurfaceVariant),
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: AppColors.cardBorder),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),

          // Indicador de envio na última pergunta
          if (currentIndex == totalQuestions - 1 && provider.isLoading)
            Container(
              margin: const EdgeInsets.only(top: 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.accent.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.accent.withOpacity(0.3)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      color: AppColors.accent,
                      strokeWidth: 2,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Enviando suas respostas...',
                    style: TextStyle(
                      color: AppColors.accent,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildOptionCard({
    required BuildContext context,
    required String optionLetter,
    required String optionText,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Card(
        color:
            isSelected ? AppColors.accent.withOpacity(0.15) : AppColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: isSelected ? AppColors.accent : AppColors.cardBorder,
            width: isSelected ? 2 : 1,
          ),
        ),
        elevation: isSelected ? 4 : 0,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Letra da opção
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: isSelected
                        ? AppColors.accent
                        : AppColors.surfaceVariant,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      optionLetter,
                      style: TextStyle(
                        color: isSelected
                            ? AppColors.background
                            : AppColors.onSurfaceVariant,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),

                // Texto da opção
                Expanded(
                  child: Text(
                    optionText,
                    style: TextStyle(
                      color:
                          isSelected ? AppColors.accent : AppColors.onSurface,
                      fontSize: 15,
                      fontWeight:
                          isSelected ? FontWeight.w600 : FontWeight.normal,
                      height: 1.4,
                    ),
                  ),
                ),

                // Checkmark
                if (isSelected)
                  Icon(
                    Icons.check_circle,
                    color: AppColors.accent,
                    size: 24,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
