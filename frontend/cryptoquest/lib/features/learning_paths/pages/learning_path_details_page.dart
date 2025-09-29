import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../features/auth/state/auth_notifier.dart';
import '../providers/learning_path_provider.dart';
import '../widgets/module_card.dart';
import '../models/learning_path_response_model.dart';
import '../theme/learning_path_colors.dart';
import '../widgets/glassmorphism_card.dart';
import '../widgets/animated_progress_ring.dart';

class LearningPathDetailsPage extends StatefulWidget {
  final String pathId;

  const LearningPathDetailsPage({
    Key? key,
    required this.pathId,
  }) : super(key: key);

  @override
  State<LearningPathDetailsPage> createState() =>
      _LearningPathDetailsPageState();
}

class _LearningPathDetailsPageState extends State<LearningPathDetailsPage> {
  LearningPathResponse? _pathDetails;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadPathDetails();
    });
  }

  void _loadPathDetails() async {
    final authProvider = Provider.of<AuthNotifier>(context, listen: false);
    final learningPathProvider =
        Provider.of<LearningPathProvider>(context, listen: false);

    final token = authProvider.token;
    if (token == null) {
      _showErrorDialog('Token de autenticação não encontrado');
      return;
    }

    final details =
        await learningPathProvider.loadPathDetails(widget.pathId, token);
    if (details != null) {
      setState(() {
        _pathDetails = details;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LearningPathColors.darkBackground,
      appBar: AppBar(
        title: Text(
          _pathDetails?.path.name ?? 'Carregando...',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
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
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Consumer<LearningPathProvider>(
        builder: (context, provider, child) {
          if (provider.isLoadingDetails) {
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
                    'Carregando detalhes...',
                    style: TextStyle(
                      color: LearningPathColors.textSecondary,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            );
          }

          if (provider.detailsErrorMessage != null) {
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
                      'Erro ao carregar trilha',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: LearningPathColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      provider.detailsErrorMessage!,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        color: LearningPathColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton.icon(
                      onPressed: _loadPathDetails,
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

          if (_pathDetails == null) {
            return Center(
              child: GlassmorphismCard(
                margin: const EdgeInsets.all(20),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.search_off,
                      size: 64,
                      color: LearningPathColors.textTertiary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Trilha não encontrada',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: LearningPathColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header da trilha
                _buildPathHeader(),

                // Estatísticas
                _buildStatsSection(),

                // Botão de ação
                _buildActionButton(),

                // Lista de módulos
                _buildModulesSection(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildPathHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        gradient: LearningPathColors.primaryGradient,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Título e dificuldade
          Row(
            children: [
              Expanded(
                child: Text(
                  _pathDetails!.path.name,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: LearningPathColors.textPrimary,
                  ),
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: LearningPathColors.getDifficultyColor(
                          _pathDetails!.path.difficulty)
                      .withOpacity(0.2),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: LearningPathColors.getDifficultyColor(
                            _pathDetails!.path.difficulty)
                        .withOpacity(0.3),
                  ),
                ),
                child: Text(
                  LearningPathColors.getDifficultyText(
                      _pathDetails!.path.difficulty),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: LearningPathColors.getDifficultyColor(
                        _pathDetails!.path.difficulty),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            _pathDetails!.path.description,
            style: const TextStyle(
              fontSize: 16,
              color: LearningPathColors.textSecondary,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Icon(
                Icons.schedule,
                color: LearningPathColors.textSecondary,
                size: 18,
              ),
              const SizedBox(width: 6),
              Text(
                _pathDetails!.path.estimatedDuration,
                style: const TextStyle(
                  fontSize: 14,
                  color: LearningPathColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(width: 20),
              Icon(
                Icons.layers,
                color: LearningPathColors.textSecondary,
                size: 18,
              ),
              const SizedBox(width: 6),
              Text(
                '${_pathDetails!.path.modules.length} módulos',
                style: const TextStyle(
                  fontSize: 14,
                  color: LearningPathColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatsSection() {
    return GlassmorphismCard(
      margin: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Progresso da Trilha',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: LearningPathColors.textPrimary,
                  ),
                ),
              ),
              AnimatedProgressRing(
                progress: _pathDetails!.progressPercentage / 100,
                size: 60,
                strokeWidth: 6,
                progressColor: _pathDetails!.progressPercentage == 100
                    ? LearningPathColors.successGreen
                    : LearningPathColors.primaryPurple,
                child: Text(
                  '${_pathDetails!.progressPercentage.toInt()}%',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: LearningPathColors.textPrimary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  'Módulos',
                  '${_pathDetails!.completedModules}/${_pathDetails!.totalModules}',
                  Icons.layers,
                  LearningPathColors.primaryPurple,
                ),
              ),
              Expanded(
                child: _buildStatItem(
                  'Missões',
                  '${_pathDetails!.completedMissions}/${_pathDetails!.totalMissions}',
                  Icons.quiz,
                  LearningPathColors.successGreen,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            height: 8,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(4),
              color: LearningPathColors.progressBackground,
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: _pathDetails!.progressPercentage / 100,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  gradient: LinearGradient(
                    colors: _pathDetails!.progressPercentage == 100
                        ? [
                            LearningPathColors.successGreen,
                            LearningPathColors.successGreenLight
                          ]
                        : [
                            LearningPathColors.primaryPurple,
                            LearningPathColors.primaryPurpleLight
                          ],
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${_pathDetails!.progressPercentage.toStringAsFixed(1)}% concluído',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: LearningPathColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(
      String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: color.withOpacity(0.3),
            ),
          ),
          child: Icon(
            icon,
            color: color,
            size: 24,
          ),
        ),
        const SizedBox(height: 12),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: LearningPathColors.textPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: LearningPathColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton() {
    final isStarted = _pathDetails!.isStarted;
    final isCompleted = _pathDetails!.isCompleted;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Consumer<LearningPathProvider>(
        builder: (context, provider, child) {
          if (isCompleted) {
            return GlassmorphismCard(
              backgroundColor: LearningPathColors.successGreen.withOpacity(0.1),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.check_circle,
                    color: LearningPathColors.successGreen,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Trilha Concluída!',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: LearningPathColors.successGreen,
                    ),
                  ),
                ],
              ),
            );
          }

          return SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: provider.isStartingPath ? null : _handleActionButton,
              icon: provider.isStartingPath
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(
                            LearningPathColors.textPrimary),
                      ),
                    )
                  : Icon(
                      isStarted ? Icons.play_arrow : Icons.play_circle_filled,
                      size: 24,
                    ),
              label: Text(
                provider.isStartingPath
                    ? 'Processando...'
                    : isStarted
                        ? 'Continuar Trilha'
                        : 'Iniciar Trilha',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: isStarted
                    ? LearningPathColors.warningOrange
                    : LearningPathColors.primaryPurple,
                foregroundColor: LearningPathColors.textPrimary,
                padding:
                    const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 4,
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildModulesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'Módulos da Trilha',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: LearningPathColors.textPrimary,
            ),
          ),
        ),
        ..._pathDetails!.path.modules.map((module) {
          final isCurrentModule =
              _pathDetails!.progress?.currentModuleId == module.id;

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: ModuleCard(
              module: module,
              progress: _pathDetails!.progress,
              isCurrentModule: isCurrentModule,
              onTap: () => _navigateToModule(module),
            ),
          );
        }).toList(),
        const SizedBox(height: 20),
      ],
    );
  }

  void _handleActionButton() async {
    final authProvider = Provider.of<AuthNotifier>(context, listen: false);
    final learningPathProvider =
        Provider.of<LearningPathProvider>(context, listen: false);

    final token = authProvider.token;
    if (token == null) {
      _showErrorDialog('Token de autenticação não encontrado');
      return;
    }

    if (!_pathDetails!.isStarted) {
      // Iniciar trilha
      final success =
          await learningPathProvider.startLearningPath(widget.pathId, token);
      if (success) {
        _loadPathDetails(); // Recarrega os detalhes
        _showSuccessDialog('Trilha iniciada com sucesso!');
      } else {
        _showErrorDialog(
            learningPathProvider.errorMessage ?? 'Erro ao iniciar trilha');
      }
    } else {
      // Continuar trilha - navegar para o primeiro módulo disponível
      final firstModule = _pathDetails!.path.modules.first;
      _navigateToModule(firstModule);
    }
  }

  void _navigateToModule(module) {
    Navigator.pushNamed(
      context,
      '/module-details',
      arguments: {
        'pathId': widget.pathId,
        'module': module,
        'progress': _pathDetails!.progress,
      },
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Erro'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showSuccessDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sucesso'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
