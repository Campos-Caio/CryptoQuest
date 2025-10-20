import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/learning_paths/services/learning_path_service.dart';
import 'package:cryptoquest/features/learning_paths/providers/learning_path_provider.dart';
import 'package:cryptoquest/features/learning_paths/models/user_path_progress_model.dart';
import 'package:cryptoquest/features/quiz/models/quiz_model.dart';
import 'package:cryptoquest/features/feedback/feedback.dart';
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

  // 🆕 COLETA DE DADOS COMPORTAMENTAIS REAIS PARA IA
  DateTime? _questionStartTime; // Momento em que a questão foi exibida
  DateTime? _quizStartTime; // Momento em que o quiz começou
  List<double> _realTimePerQuestion =
      []; // Tempo real gasto em cada questão (segundos)
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

          // 🆕 Inicializar coleta de dados comportamentais
          _quizStartTime = DateTime.now();
          _questionStartTime = DateTime.now(); // Primeira questão começa agora
          _realTimePerQuestion = [];
          _attemptsPerQuestion = List.filled(loadedQuiz.questions.length, 0);
          _currentQuestionAttempts = 0;

          print('🎯 [IA] Quiz iniciado às ${_quizStartTime}');
          print('🎯 [IA] Timer da primeira questão iniciado');
        });
      }
    }
  }

  // NOVO MÉTODO: Processar seleção de resposta
  void _selectAnswer(int answerIndex) {
    if (_isAnswerSubmitted) return; // Evita múltiplas seleções

    // 🆕 CALCULAR TEMPO REAL gasto na questão
    if (_questionStartTime != null) {
      final elapsed = DateTime.now().difference(_questionStartTime!);
      final timeInSeconds =
          elapsed.inMilliseconds / 1000.0; // Precisão em milissegundos
      _realTimePerQuestion.add(timeInSeconds);

      print(
          '🎯 [IA] Questão ${currentQuestionIndex + 1}: ${timeInSeconds.toStringAsFixed(2)}s');
    }

    // 🆕 REGISTRAR tentativa
    _currentQuestionAttempts++;
    _attemptsPerQuestion[currentQuestionIndex] = _currentQuestionAttempts;

    print(
        '🎯 [IA] Tentativa #${_currentQuestionAttempts} na questão ${currentQuestionIndex + 1}');

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

        // 🆕 RESETAR timer e tentativas para próxima questão
        _questionStartTime = DateTime.now();
        _currentQuestionAttempts = 0;

        print('🎯 [IA] Avançou para questão ${currentQuestionIndex + 1}');
        print('🎯 [IA] Timer da questão ${currentQuestionIndex + 1} iniciado');
      });
    } else {
      // Última pergunta - submeter o quiz
      print('🎯 [IA] Finalizando quiz...');
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

          // 🆕 USAR DADOS COMPORTAMENTAIS REAIS coletados durante o quiz
          print('🎯 [IA] ===== RESUMO DOS DADOS COLETADOS =====');
          print(
              '🎯 [IA] Tempo total do quiz: ${DateTime.now().difference(_quizStartTime!).inSeconds}s');
          print('🎯 [IA] Tempo por questão (real): $_realTimePerQuestion');
          print('🎯 [IA] Tentativas por questão: $_attemptsPerQuestion');
          print('🎯 [IA] ===========================================');

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

          print('🎯 [IA] Confiança estimada: $confidenceLevels');

          result = await learningPathService.completeMission(
            widget.pathId!,
            widget.missionId,
            selectedAnswers,
            authNotifier.token!,
            timePerQuestion: _realTimePerQuestion, // ✅ DADOS REAIS!
            confidenceLevels:
                confidenceLevels, // ⚠️ Estimado, mas melhor que fake
            hintsUsed: hintsUsed, // ⚠️ Por enquanto 0 (sem sistema de dicas)
            attemptsPerQuestion: _attemptsPerQuestion, // ✅ DADOS REAIS!
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

          // 🔄 ATUALIZAR MISSION NOTIFIER COM DADOS CORRETOS
          if (widget.pathId != null && result != null) {
            final missionNotifier =
                Provider.of<MissionNotifier>(context, listen: false);
            missionNotifier.setLastCompletedMission(result);

            // 🔄 ATUALIZAR LEARNING PATH PROVIDER COM PROGRESSO ATUALIZADO
            final learningPathProvider =
                Provider.of<LearningPathProvider>(context, listen: false);

            // 🔍 DEBUG: Verificar se o progresso está sendo retornado
            print('🔍 [DEBUG] Result keys: ${result.keys}');
            print('🔍 [DEBUG] Progress data: ${result['progress']}');

            if (result['progress'] != null) {
              try {
                final progress = UserPathProgress.fromJson(result['progress']);
                print(
                    '🔍 [DEBUG] Progress parsed successfully: ${progress.completedMissions}');
                learningPathProvider.updateProgress(widget.pathId!, progress);
                print('✅ [DEBUG] Progress updated in LearningPathProvider');
              } catch (e) {
                print('❌ [DEBUG] Error parsing progress: $e');
              }
            } else {
              print('⚠️ [DEBUG] No progress data in result');
            }
          }

          // ⚡ OTIMIZAÇÃO: Backend já processou tudo - apenas atualizar dados locais!
          // Backend retorna: points, xp, total_points, total_xp, progress
          // Não precisa fazer novas chamadas à API

          // Atualizar perfil local com dados que já vieram do backend
          if (result != null &&
              result.containsKey('xp') &&
              result.containsKey('points')) {
            // Calcular totais (backend pode retornar total_xp/total_points OU xp_earned/points_earned)
            final totalXp = result['total_xp'] ??
                (authNotifier.userProfile?.xp ?? 0) + (result['xp'] ?? 0);
            final totalPoints = result['total_points'] ??
                (authNotifier.userProfile?.points ?? 0) +
                    (result['points'] ?? 0);

            authNotifier.updateLocalProfile(
              points: totalPoints,
              xp: totalXp,
            );

            print(
                '⚡ [OTIMIZAÇÃO] Perfil atualizado localmente sem chamada API');
            print(
                '   Points: ${authNotifier.userProfile?.points} → $totalPoints');
            print('   XP: ${authNotifier.userProfile?.xp} → $totalXp');
          }

          // ❌ REMOVIDO: _processRewardsAndBadges() - Backend já processou!
          // ❌ REMOVIDO: refreshUserProfile() - Dados já atualizados localmente!
          // ECONOMIA: ~3.7 segundos! ⚡

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

  // ⚡ OTIMIZAÇÃO: Métodos _processRewardsAndBadges e _showBadgeNotification REMOVIDOS
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
    final xpGained = (result?['xp_earned'] ?? result?['xp'] ?? 0) as int;
    final pointsGained =
        (result?['points_earned'] ?? result?['points'] ?? 0) as int;
    final currentXP = (result?['total_xp'] ?? userProfile?.xp ?? 0) as int;
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

    // Exibir novo sistema de feedback
    RewardSummarySheet.show(
      context: context,
      rewardData: rewardData,
      onContinue: () {
        // Retorna o resultado para a tela anterior
        Navigator.of(context).pop({
          'score': percentage.round(),
          'success': percentage >= 70,
          'points': result?['points'] ?? 0,
          'level': result?['level'] ?? 1,
          'answers': selectedAnswers,
        });
      },
      onViewProfile: () {
        Navigator.pushNamed(context, '/profile');
      },
      onViewBadges: percentage >= 70
          ? () {
              Navigator.pushNamed(context, '/rewards');
            }
          : null,
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
