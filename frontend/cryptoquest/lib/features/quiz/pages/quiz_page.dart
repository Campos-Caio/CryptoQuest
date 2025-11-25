import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/learning_paths/services/learning_path_service.dart';
import 'package:cryptoquest/features/learning_paths/providers/learning_path_provider.dart';
import 'package:cryptoquest/features/learning_paths/models/user_path_progress_model.dart';
import 'package:cryptoquest/features/quiz/models/quiz_model.dart';
import 'package:cryptoquest/features/feedback/feedback.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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

  DateTime? _questionStartTime;
  List<double> _realTimePerQuestion = [];
  List<int> _attemptsPerQuestion = []; // Número de tentativas por questão
  int _currentQuestionAttempts = 0; // Tentativas na questão atual

  // Dados que podem ser coletados futuramente:
  // List<double> _confidenceLevels = []; // Nível de confiança do usuário (0-1)
  // List<int> _hintsUsed = []; // Número de dicas usadas por questão

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

          _questionStartTime = DateTime.now();
          _realTimePerQuestion = [];
          _attemptsPerQuestion = List.filled(loadedQuiz.questions.length, 0);
          _currentQuestionAttempts = 0;
        });
      }
    }
  }

    void _selectAnswer(int answerIndex) {
      if (_isAnswerSubmitted) return;

      if (_questionStartTime != null) {
        final elapsed = DateTime.now().difference(_questionStartTime!);
        final timeInSeconds = elapsed.inMilliseconds / 1000.0;
        _realTimePerQuestion.add(timeInSeconds);
      }

    _currentQuestionAttempts++;
    _attemptsPerQuestion[currentQuestionIndex] = _currentQuestionAttempts;

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

    // Feedback háptico
    if (_isAnswerCorrect) {
      HapticFeedback.mediumImpact();
    } else {
      HapticFeedback.heavyImpact();
    }

    // Mostrar feedback visual com Lottie (opcional - aparece como overlay)
    _showAnswerFeedbackOverlay(_isAnswerCorrect);

    // Aguardar 2 segundos para o usuário ver o resultado
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        _nextQuestion();
      }
    });
  }

  /// Mostra feedback visual discreto no canto da tela
  void _showAnswerFeedbackOverlay(bool isCorrect) {
    // Usar SnackBar em vez de overlay para não sobrepor o conteúdo
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 24,
              height: 24,
              child: isCorrect
                  ? LottieAnimations.successCheck(size: 24)
                  : LottieAnimations.errorCross(size: 24),
            ),
            const SizedBox(width: 12),
            Text(
              isCorrect ? 'Correto!' : 'Incorreto',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        backgroundColor: isCorrect ? Colors.green : Colors.red,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.only(
          bottom: 100, // Posicionar acima dos botões
          left: 16,
          right: 16,
        ),
        duration: const Duration(milliseconds: 1500),
      ),
    );
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

        _questionStartTime = DateTime.now();
        _currentQuestionAttempts = 0;

      });
    } else {
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


          // Preparar dados de confiança (por enquanto estimado, mas estrutura pronta)
          // Estimativa baseada em tempo: resposta rápida = mais confiança
          List<double> confidenceLevels = _realTimePerQuestion.map((time) {
            if (time < 5) return 0.9; // Muito rápido = muito confiante
            if (time < 10) return 0.75; // Rápido = confiante
            if (time < 20) return 0.6; // Normal = moderado
            if (time < 30) return 0.45; // Lento = pouco confiante
            return 0.3; // Muito lento = muito pouco confiante
          }).toList();

          // Preparar dados de dicas (por enquanto 0, mas estrutura pronta)
          List<int> hintsUsed = List.filled(selectedAnswers.length, 0);


          result = await learningPathService.completeMission(
            widget.pathId!,
            widget.missionId,
            selectedAnswers,
            authNotifier.token!,
            timePerQuestion: _realTimePerQuestion,
            confidenceLevels: confidenceLevels,
            hintsUsed: hintsUsed,
            attemptsPerQuestion: _attemptsPerQuestion,
          );
          success = result['success'] == true;
        } else {
          // Usar serviço de missões diárias (comportamento original)
          final missionNotifier =
              Provider.of<MissionNotifier>(context, listen: false);
          result = await missionNotifier.completeMission(
            widget.missionId,
            selectedAnswers,
            authNotifier.token!,
          );
          success = result != null;
        }

        if (mounted) {
          // Calcular pontuação localmente
          int correctAnswers = 0;
          for (int i = 0; i < quiz!.questions.length; i++) {
            if (selectedAnswers[i] == quiz!.questions[i].correctAnswerIndex) {
              correctAnswers++;
            }
          }
          double percentage = (correctAnswers / quiz!.questions.length) * 100;

          if (success && widget.pathId != null && result != null) {
            final missionNotifier =
                Provider.of<MissionNotifier>(context, listen: false);
            missionNotifier.setLastCompletedMission(result);

            final learningPathProvider =
                Provider.of<LearningPathProvider>(context, listen: false);

            if (result['progress'] != null) {
              try {
                final progress = UserPathProgress.fromJson(result['progress']);
                learningPathProvider.updateProgress(widget.pathId!, progress);
              } catch (e) {
                // Error parsing progress
              }
            }
          }

          if (success && result != null && percentage >= 70) {
            final updatedPoints = result['points'] as int?;
            final updatedXp = result['xp'] as int?;
            final updatedLevel = result['level'] as int?;
            final updatedStreak = result['current_streak'] as int?;
            final updatedBadges = result['badges'] as List<dynamic>?;

            if (updatedPoints != null || updatedXp != null) {
              authNotifier.updateLocalProfile(
                points: updatedPoints,
                xp: updatedXp,
                level: updatedLevel,
                currentStreak: updatedStreak,
                badges: updatedBadges?.map((e) => e.toString()).toList(),
              );
            }
          }
          _showResultDialog(percentage);
        }
      }
    } catch (e) {
      if (mounted) {
        String errorMessage = 'Erro ao enviar respostas';
        String errorString = e.toString().toLowerCase();

        // Debug: imprimir o erro real para console

        if (errorString.contains('já foi concluída hoje') ||
            errorString.contains('409') ||
            errorString.contains('conflict') ||
            errorString.contains('missão já concluída') ||
            errorString.contains('não está disponível hoje')) {
          errorMessage =
              'Esta missão já foi concluída hoje. Tente novamente amanhã!';
        }
        // Agora o backend não lança erro, apenas retorna resultado indicando falha
        // O feedback será mostrado na tela de resultados

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

  // Backend já processa tudo (badges, recompensas) em background
  // Badges aparecem automaticamente quando backend terminar o processamento
  // ECONOMIA: ~3.2 segundos por não fazer POST /rewards/award/mission redundante

  void _showResultDialog(double percentage) {
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final missionNotifier =
        Provider.of<MissionNotifier>(context, listen: false);
    final result = missionNotifier.lastCompletedMission;
    final userProfile = authNotifier.userProfile;

    // Preparar dados de feedback com informações mais ricas
    // Baseado nos logs do servidor, os campos corretos são:
    final xpGained = percentage >= 70
        ? ((result?['xp_gained'] ??
            result?['xp_earned'] ??
            result?['xp'] ??
            0) as int)
        : 0;
    final pointsGained = percentage >= 70
        ? ((result?['points_gained'] ??
            result?['points_earned'] ??
            result?['points'] ??
            0) as int)
        : 0;
    final currentXP = percentage >= 70
        ? ((result?['total_xp'] ?? result?['xp'] ?? userProfile?.xp ?? 0) as int)
        : (userProfile?.xp ?? 0);
    final previousXP = currentXP - xpGained;


    // Calcular nível baseado no novo sistema de XP
    final currentLevel = _calculateLevelFromXP(currentXP);
    final previousLevel = _calculateLevelFromXP(previousXP);
    final leveledUp = currentLevel > previousLevel;

    // Determinar mensagem baseada no desempenho
    String message;
    if (percentage >= 90) {
      message = 'Perfeito! Você é um verdadeiro especialista!';
    } else if (percentage >= 80) {
      message = 'Excelente trabalho! Continue assim!';
    } else if (percentage >= 70) {
      message = 'Muito bom! Você está no caminho certo!';
    } else if (percentage >= 50) {
      message = 'Bom esforço! Continue estudando!';
    } else {
      message = 'Não desista! Tente novamente!';
    }

    final rewardData = RewardFeedbackModel(
      xpGained: xpGained,
      pointsGained: pointsGained,
      previousXP: previousXP,
      currentXP: currentXP,
      previousLevel: previousLevel,
      currentLevel: currentLevel,
      leveledUp: leveledUp,
      badgesEarned: [], // Será populado pelo processamento de badges
      streakDays: userProfile?.currentStreak ?? 0,
      quizPercentage: percentage,
      isSuccess: percentage >= 70,
      message: message,
    );

    // Exibir novo sistema central de feedback
    FeedbackService.showQuizFeedback(
      context: context,
      quizResult: {
        'score': percentage.round(),
        'success': percentage >= 70,
        'points': result?['points'] ?? 0,
        'level': result?['level'] ?? 1,
        'answers': selectedAnswers,
        'onRetry': percentage < 70 ? () {
          // Recarregar o quiz para tentar novamente
          _loadQuiz();
          setState(() {
            currentQuestionIndex = 0;
            selectedAnswers = List.filled(quiz!.questions.length, -1);
            _selectedAnswerIndex = null;
            _correctAnswerIndex = null;
            _isAnswerSubmitted = false;
            _isAnswerCorrect = false;
            _questionStartTime = DateTime.now();
            _realTimePerQuestion = [];
            _attemptsPerQuestion = List.filled(quiz!.questions.length, 0);
            _currentQuestionAttempts = 0;
          });
        } : null,
      },
      rewardData: rewardData,
      onComplete: () {
        // Para falha, o usuário deve escolher "Tentar Novamente" ou "Continuar"
        if (percentage >= 70) {
          // Retorna o resultado para a tela anterior
          Navigator.of(context).pop({
            'score': percentage.round(),
            'success': percentage >= 70,
            'points': result?['points'] ?? 0,
            'level': result?['level'] ?? 1,
            'answers': selectedAnswers,
          });
        }
        // Se falhou, não fechar automaticamente - deixar o usuário escolher
      },
    );
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

  /// Calcula o nível baseado no XP total usando o novo sistema rebalanceado
  int _calculateLevelFromXP(int totalXP) {
    // Sistema de níveis rebalanceado (mesmo do backend)
    final levelRequirements = {
      1: 0, // Nível 1: 0 XP
      2: 500, // Nível 2: 500 XP total
      3: 1000, // Nível 3: 1000 XP total
      4: 1500, // Nível 4: 1500 XP total
      5: 2000, // Nível 5: 2000 XP total
      6: 2500, // Nível 6: 2500 XP total
      7: 3000, // Nível 7: 3000 XP total
      8: 3500, // Nível 8: 3500 XP total
      9: 4000, // Nível 9: 4000 XP total
      10: 4500, // Nível 10: 4500 XP total
      11: 5250, // Nível 11: 5250 XP total
      12: 6000, // Nível 12: 6000 XP total
      13: 6750, // Nível 13: 6750 XP total
      14: 7500, // Nível 14: 7500 XP total
      15: 8250, // Nível 15: 8250 XP total
      16: 9000, // Nível 16: 9000 XP total
      17: 9750, // Nível 17: 9750 XP total
      18: 10500, // Nível 18: 10500 XP total
      19: 11250, // Nível 19: 11250 XP total
      20: 12000, // Nível 20: 12000 XP total
      21: 13000, // Nível 21: 13000 XP total
      22: 14000, // Nível 22: 14000 XP total
      23: 15000, // Nível 23: 15000 XP total
      24: 16000, // Nível 24: 16000 XP total
      25: 17000, // Nível 25: 17000 XP total
    };

    int level = 1;

    for (int requiredLevel = 2; requiredLevel <= 25; requiredLevel++) {
      if (totalXP >= levelRequirements[requiredLevel]!) {
        level = requiredLevel;
      } else {
        break;
      }
    }

    return level;
  }
}
