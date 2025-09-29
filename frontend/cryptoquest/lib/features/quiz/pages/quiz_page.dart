import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/learning_paths/services/learning_path_service.dart';
import 'package:cryptoquest/features/quiz/models/quiz_model.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class QuizPage extends StatefulWidget {
  final String missionId;
  final String quizId;
  final String missionTitle;
  final String? pathId; // Para missões de trilhas de aprendizado
  final bool isLearningPathMission; // Flag para identificar tipo de missão

  QuizPage({
    Key? key,
    required this.missionId,
    required this.quizId,
    required this.missionTitle,
    this.pathId,
    this.isLearningPathMission = false,
  }) : super(key: key);

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  List<int> selectedAnswers = [];
  Quiz? quiz;
  int currentQuestionIndex = 0;
  bool isSubmitting = false;

  // NOVOS ESTADOS PARA FEEDBACK VISUAL
  int? _selectedAnswerIndex; // Índice da resposta selecionada
  int? _correctAnswerIndex; // Índice da resposta correta
  bool _isAnswerSubmitted = false; // Se a resposta foi enviada
  bool _isAnswerCorrect = false; // Se a resposta está correta

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

  // NOVO MÉTODO: Processar seleção de resposta
  void _selectAnswer(int answerIndex) {
    if (_isAnswerSubmitted) return; // Evita múltiplas seleções

    setState(() {
      _selectedAnswerIndex = answerIndex;
      _isAnswerSubmitted = true;

      // Verificar se a resposta está correta
      final currentQuestion = quiz!.questions[currentQuestionIndex];
      _correctAnswerIndex = currentQuestion.correctAnswerIndex;
      _isAnswerCorrect = (answerIndex == _correctAnswerIndex);

      // Salvar a resposta selecionada
      selectedAnswers[currentQuestionIndex] = answerIndex;
    });

    // Aguardar 2 segundos para o usuário ver o resultado
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        _nextQuestion();
      }
    });
  }

  // NOVO MÉTODO: Avançar para próxima pergunta
  void _nextQuestion() {
    if (currentQuestionIndex < quiz!.questions.length - 1) {
      setState(() {
        currentQuestionIndex++;
        _selectedAnswerIndex = null;
        _correctAnswerIndex = null;
        _isAnswerSubmitted = false;
        _isAnswerCorrect = false;
      });
    } else {
      // Última pergunta - submeter o quiz
      _submitQuiz();
    }
  }

  // NOVO MÉTODO: Obter cor da opção baseada no status
  Color _getOptionColor(int optionIndex) {
    if (!_isAnswerSubmitted) {
      return const Color(0xFF424242); // Neutro
    }

    if (optionIndex == _correctAnswerIndex) {
      return Colors.green[400]!; // Sempre verde se for a correta
    }

    if (optionIndex == _selectedAnswerIndex && !_isAnswerCorrect) {
      return Colors.red[400]!; // Vermelho se selecionou incorreta
    }

    return const Color(0xFF424242); // Neutro para outras opções
  }

  // NOVO MÉTODO: Obter ícone da opção
  Icon? _getOptionIcon(int optionIndex) {
    if (!_isAnswerSubmitted) return null;

    if (optionIndex == _correctAnswerIndex) {
      return const Icon(Icons.check_circle, color: Colors.white, size: 24);
    }

    if (optionIndex == _selectedAnswerIndex && !_isAnswerCorrect) {
      return const Icon(Icons.cancel, color: Colors.white, size: 24);
    }

    return null;
  }

  // NOVO MÉTODO: Obter cor do texto da opção
  Color _getOptionTextColor(int optionIndex) {
    if (!_isAnswerSubmitted) {
      return const Color(0xFFE0E0E0); // Neutro
    }

    return Colors.white; // Branco para todas as opções após seleção
  }

  Future<void> _submitQuiz() async {
    if (selectedAnswers.contains(-1)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Responda todas as perguntas!')),
      );
      return;
    }

    try {
      setState(() {
        isSubmitting = true;
      });

      final authNotifier = Provider.of<AuthNotifier>(context, listen: false);

      if (authNotifier.token != null) {
        bool success = false;
        Map<String, dynamic>? result;

        if (widget.isLearningPathMission && widget.pathId != null) {
          // Usar serviço de trilhas de aprendizado
          final learningPathService = LearningPathService();
          result = await learningPathService.completeMission(
            widget.pathId!,
            widget.missionId,
            selectedAnswers,
            authNotifier.token!,
          );
          success = result['success'] == true;
        } else {
          // Usar serviço de missões diárias (comportamento original)
          final missionNotifier =
              Provider.of<MissionNotifier>(context, listen: false);
          success = await missionNotifier.completeMission(
            widget.missionId,
            selectedAnswers,
            authNotifier.token!,
          );
        }

        if (success && mounted) {
          // Calcular pontuação
          int correctAnswers = 0;
          for (int i = 0; i < quiz!.questions.length; i++) {
            if (selectedAnswers[i] == quiz!.questions[i].correctAnswerIndex) {
              correctAnswers++;
            }
          }
          double percentage = (correctAnswers / quiz!.questions.length) * 100;

          // Mostrar resultado
          _showResultDialog(percentage);
        }
      }
    } catch (e) {
      if (mounted) {
        String errorMessage = 'Erro ao enviar respostas';
        String errorString = e.toString().toLowerCase();

        // Debug: imprimir o erro real para console
        print('Erro capturado: $e');
        print('Tipo do erro: ${e.runtimeType}');

        if (errorString.contains('já foi concluída hoje') ||
            errorString.contains('409') ||
            errorString.contains('conflict') ||
            errorString.contains('missão já concluída') ||
            errorString.contains('não está disponível hoje')) {
          errorMessage =
              'Esta missão já foi concluída hoje. Tente novamente amanhã!';
        } else if (errorString.contains('acertou')) {
          errorMessage = e.toString();
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Colors.orange,
            duration: const Duration(seconds: 4),
            action: SnackBarAction(
              label: 'OK',
              textColor: Colors.white,
              onPressed: () {
                ScaffoldMessenger.of(context).hideCurrentSnackBar();
              },
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          isSubmitting = false;
        });
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
                      // Retorna o resultado para a tela anterior (trilhas)
                      Navigator.of(context).pop({
                        'score': percentage.round(),
                        'success': percentage >= 70,
                        'points': result?['points'] ?? 0,
                        'level': result?['level'] ?? 1,
                        'answers': selectedAnswers, // Adiciona as respostas
                      });
                    },
                    child: const Text("OK"))
              ],
            ));
  }

  // NOVO WIDGET: Opção de resposta com feedback visual
  Widget _buildAnswerOption(int optionIndex, String optionText) {
    final isSelected = _selectedAnswerIndex == optionIndex;
    final isSubmitted = _isAnswerSubmitted;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: isSubmitted ? null : () => _selectAnswer(optionIndex),
        borderRadius: BorderRadius.circular(12),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _getOptionColor(optionIndex),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? Colors.blue : Colors.grey[400]!,
              width: isSelected ? 2 : 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              // Ícone de feedback (aparece após seleção)
              if (_getOptionIcon(optionIndex) != null)
                Padding(
                  padding: const EdgeInsets.only(right: 12),
                  child: _getOptionIcon(optionIndex)!,
                ),

              // Texto da opção
              Expanded(
                child: Text(
                  optionText,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight:
                        isSelected ? FontWeight.bold : FontWeight.normal,
                    color: _getOptionTextColor(optionIndex),
                  ),
                  textAlign: TextAlign.center,
                ),
              ),

              // Indicador de seleção
              if (isSelected && !isSubmitted)
                const Icon(Icons.radio_button_checked, color: Colors.blue),
            ],
          ),
        ),
      ),
    );
  }

  // NOVO LAYOUT: Uma pergunta por vez com feedback visual
  Widget _buildQuestionView() {
    final currentQuestion = quiz!.questions[currentQuestionIndex];

    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: [
          // Cabeçalho da pergunta
          Container(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                // Progresso
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Pergunta ${currentQuestionIndex + 1} de ${quiz!.questions.length}',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[400],
                      ),
                    ),
                    Text(
                      '${((currentQuestionIndex + 1) / quiz!.questions.length * 100).round()}%',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[400],
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Barra de progresso
                LinearProgressIndicator(
                  value: (currentQuestionIndex + 1) / quiz!.questions.length,
                  backgroundColor: const Color(0xFF424242),
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[400]!),
                  minHeight: 8,
                ),
              ],
            ),
          ),

          // Título da pergunta
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF424242),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              currentQuestion.text,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          ),

          const SizedBox(height: 30),

          // Opções de resposta
          Expanded(
            child: ListView.builder(
              itemCount: currentQuestion.options.length,
              itemBuilder: (context, index) {
                return _buildAnswerOption(
                  index,
                  currentQuestion.options[index].text,
                );
              },
            ),
          ),

          // Mensagem de feedback
          if (_isAnswerSubmitted)
            Container(
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _isAnswerCorrect ? Colors.green[100] : Colors.red[100],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _isAnswerCorrect ? Colors.green : Colors.red,
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    _isAnswerCorrect ? Icons.check_circle : Icons.cancel,
                    color: _isAnswerCorrect ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _isAnswerCorrect ? 'Correto!' : 'Incorreto!',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: _isAnswerCorrect
                          ? Colors.green[800]
                          : Colors.red[800],
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: Text(
          widget.missionTitle,
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.deepPurple[700],
        iconTheme: IconThemeData(color: Colors.white),
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

          if (isSubmitting) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(
                    color: Colors.deepPurple,
                  ),
                  SizedBox(
                    height: 16,
                  ),
                  Text(
                    "Processando respostas...",
                    style: TextStyle(color: Colors.white),
                  )
                ],
              ),
            );
          }

          return _buildQuestionView();
        },
      ),
    );
  }
}
