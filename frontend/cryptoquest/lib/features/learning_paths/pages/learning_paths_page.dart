import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/learning_path_provider.dart';
import '../widgets/learning_path_card.dart';
import '../theme/learning_path_colors.dart';
import '../widgets/glassmorphism_card.dart';

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
    provider.loadLearningPaths();
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
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
              itemCount: provider.learningPaths.length,
              itemBuilder: (context, index) {
                final learningPath = provider.learningPaths[index];
                final progress = provider.getPathProgress(learningPath.id);

                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: LearningPathCard(
                    learningPath: learningPath,
                    progress: progress,
                    onTap: () => _navigateToPathDetails(learningPath.id),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }

  void _navigateToPathDetails(String pathId) {
    Navigator.pushNamed(
      context,
      '/learning-path-details',
      arguments: pathId,
    );
  }
}
