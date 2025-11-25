import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/learning_path_provider.dart';
import '../widgets/learning_path_card.dart';
import '../theme/learning_path_colors.dart';
import '../widgets/glassmorphism_card.dart';
import '../widgets/ai_recommendation_card.dart';
import '../../auth/state/auth_notifier.dart';
import '../models/learning_path_model.dart';

class LearningPathsPage extends StatefulWidget {
  const LearningPathsPage({Key? key}) : super(key: key);

  @override
  State<LearningPathsPage> createState() => _LearningPathsPageState();
}

class _LearningPathsPageState extends State<LearningPathsPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadLearningPaths();
    });
  }

  void _loadLearningPaths() {
    final provider = Provider.of<LearningPathProvider>(context, listen: false);
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);

    provider.loadLearningPaths();

    // Carregar progresso do usuário para ordenação correta
    if (authNotifier.token != null) {
      provider.loadUserProgress(authNotifier.token);
      provider.loadRecommendedLearningPaths(authNotifier.token!, limit: 1);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LearningPathColors.darkBackground,
      appBar: AppBar(
        title: const Text(
          'Trilhas de Aprendizado',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        backgroundColor: Colors.transparent,
        foregroundColor: LearningPathColors.textPrimary,
        elevation: 0,
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LearningPathColors.primaryGradient,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadLearningPaths,
            tooltip: 'Atualizar trilhas',
          ),
        ],
      ),
      body: Consumer<LearningPathProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(
                      LearningPathColors.primaryPurple,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Carregando trilhas...',
                    style: TextStyle(
                      color: LearningPathColors.textSecondary,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            );
          }

          if (provider.errorMessage != null) {
            return Center(
              child: GlassmorphismCard(
                margin: const EdgeInsets.all(20),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 64,
                      color: LearningPathColors.errorRed,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Erro ao carregar trilhas',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: LearningPathColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      provider.errorMessage!,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        color: LearningPathColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton.icon(
                      onPressed: _loadLearningPaths,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Tentar Novamente'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: LearningPathColors.primaryPurple,
                        foregroundColor: LearningPathColors.textPrimary,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }

          if (provider.learningPaths.isEmpty) {
            return Center(
              child: GlassmorphismCard(
                margin: const EdgeInsets.all(20),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.school_outlined,
                      size: 64,
                      color: LearningPathColors.textTertiary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Nenhuma trilha encontrada',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: LearningPathColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Não há trilhas de aprendizado disponíveis no momento.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        color: LearningPathColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              _loadLearningPaths();
            },
            color: LearningPathColors.primaryPurple,
            backgroundColor: LearningPathColors.cardBackground,
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
              children: [
                if (provider.aiRecommendations.isNotEmpty) ...[
                  Padding(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
                    child: Row(
                      children: [
                        Icon(
                          Icons.psychology,
                          color: LearningPathColors.primaryPurple,
                          size: 24,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Recomendações Inteligentes',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: LearningPathColors.textPrimary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Lista de recomendações
                  ...provider.aiRecommendations.map((recommendation) {
                    return AIRecommendationCard(
                      recommendation: recommendation,
                      showFullReasoning: true,
                      onTap: () {
                        final pathId = recommendation['path_id'] as String?;
                        if (pathId != null) {
                          _navigateToPathDetails(pathId);
                        }
                      },
                    );
                  }).toList(),

                  // Separador
                  Container(
                    margin: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 24),
                    height: 1,
                    color: LearningPathColors.textSecondary.withOpacity(0.3),
                  ),

                  Padding(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    child: Text(
                      'Todas as Trilhas',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: LearningPathColors.textPrimary,
                      ),
                    ),
                  ),
                ],

                // Lista normal de trilhas (ordenada)
                ..._getSortedLearningPaths(provider).map((learningPath) {
                  final progress = provider.getPathProgress(learningPath.id);

                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: LearningPathCard(
                      learningPath: learningPath,
                      progress: progress,
                      onTap: () => _navigateToPathDetails(learningPath.id),
                    ),
                  );
                }).toList(),
              ],
            ),
          );
        },
      ),
    );
  }

  /// Ordena as trilhas conforme as regras especificadas:
  /// 1. Trilhas iniciadas primeiro
  /// 2. Entre trilhas iniciadas, ordena por porcentagem de progresso (maior primeiro)
  /// 3. Trilhas não iniciadas ordenadas por dificuldade (Iniciante → Intermediário → Avançado)
  List<LearningPath> _getSortedLearningPaths(LearningPathProvider provider) {
    final paths = List<LearningPath>.from(provider.learningPaths);

    // Função auxiliar para obter a ordem numérica da dificuldade
    int getDifficultyOrder(String difficulty) {
      switch (difficulty.toLowerCase()) {
        case 'beginner':
        case 'iniciante':
          return 1;
        case 'intermediate':
        case 'intermediario':
        case 'intermediário':
          return 2;
        case 'advanced':
        case 'avancado':
        case 'avançado':
          return 3;
        default:
          return 0; // Dificuldade desconhecida vai para o final
      }
    }

    paths.sort((a, b) {
      final progressA = provider.getPathProgress(a.id);
      final progressB = provider.getPathProgress(b.id);

      final isStartedA = progressA != null;
      final isStartedB = progressB != null;

      // 1. Priorizar trilhas iniciadas
      if (isStartedA && !isStartedB) {
        return -1; // A vem antes de B
      } else if (!isStartedA && isStartedB) {
        return 1; // B vem antes de A
      }

      // 2. Se ambas estão iniciadas, ordenar por porcentagem de progresso (maior primeiro)
      if (isStartedA && isStartedB) {
        final progressPercentageA = progressA.progressPercentage;
        final progressPercentageB = progressB.progressPercentage;

        // Ordenar por progresso decrescente (maior primeiro)
        final progressComparison =
            progressPercentageB.compareTo(progressPercentageA);
        if (progressComparison != 0) {
          return progressComparison;
        }
        // Se o progresso for igual, manter ordem original ou ordenar por dificuldade
        final difficultyOrderA = getDifficultyOrder(a.difficulty);
        final difficultyOrderB = getDifficultyOrder(b.difficulty);
        return difficultyOrderA.compareTo(difficultyOrderB);
      }

      // 3. Se nenhuma está iniciada, ordenar por dificuldade (Iniciante → Intermediário → Avançado)
      final difficultyOrderA = getDifficultyOrder(a.difficulty);
      final difficultyOrderB = getDifficultyOrder(b.difficulty);
      return difficultyOrderA.compareTo(difficultyOrderB);
    });

    return paths;
  }

  void _navigateToPathDetails(String pathId) {
    Navigator.pushNamed(
      context,
      '/learning-path-details',
      arguments: pathId,
    );
  }
}
