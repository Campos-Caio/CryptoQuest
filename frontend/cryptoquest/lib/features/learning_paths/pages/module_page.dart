import 'package:flutter/material.dart';
import '../../../features/quiz/pages/quiz_page.dart';
import '../widgets/mission_list_item.dart';
import '../models/learning_path_model.dart';
import '../models/user_path_progress_model.dart';
import '../theme/learning_path_colors.dart';
import '../widgets/glassmorphism_card.dart';

class ModulePage extends StatefulWidget {
  final String pathId;
  final Module module;
  final UserPathProgress? progress;

  const ModulePage({
    Key? key,
    required this.pathId,
    required this.module,
    this.progress,
  }) : super(key: key);

  @override
  State<ModulePage> createState() => _ModulePageState();
}

class _ModulePageState extends State<ModulePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LearningPathColors.darkBackground,
      appBar: AppBar(
        title: Text(
          widget.module.name,
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
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header do módulo
            _buildModuleHeader(),

            // Descrição do módulo
            _buildModuleDescription(),

            // Status do módulo
            _buildModuleStatus(),

            // Lista de missões
            _buildMissionsList(),
          ],
        ),
      ),
    );
  }

  Widget _buildModuleHeader() {
    final isCompleted =
        widget.progress?.completedModules.contains(widget.module.id) ?? false;
    final isCurrentModule =
        widget.progress?.currentModuleId == widget.module.id;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: isCompleted
            ? LearningPathColors.successGradient
            : isCurrentModule
                ? LearningPathColors.primaryGradient
                : LinearGradient(
                    colors: [
                      LearningPathColors.textTertiary,
                      LearningPathColors.textTertiary.withOpacity(0.7),
                    ],
                  ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: LearningPathColors.textPrimary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  isCompleted
                      ? Icons.check_circle
                      : isCurrentModule
                          ? Icons.play_circle_filled
                          : Icons.circle_outlined,
                  color: LearningPathColors.textPrimary,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Módulo ${widget.module.order}',
                      style: const TextStyle(
                        fontSize: 14,
                        color: LearningPathColors.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.module.name,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: LearningPathColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Icon(
                Icons.quiz,
                color: LearningPathColors.textSecondary,
                size: 18,
              ),
              const SizedBox(width: 6),
              Text(
                '${widget.module.missions.length} missões',
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

  Widget _buildModuleDescription() {
    return GlassmorphismCard(
      margin: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Sobre este módulo',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: LearningPathColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            widget.module.description,
            style: TextStyle(
              fontSize: 14,
              color: LearningPathColors.textSecondary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModuleStatus() {
    final isCompleted =
        widget.progress?.completedModules.contains(widget.module.id) ?? false;
    final isCurrentModule =
        widget.progress?.currentModuleId == widget.module.id;
    final completedMissions = widget.module.missions
        .where((mission) =>
            widget.progress?.completedMissions.contains(mission.id) ?? false)
        .length;

    return GlassmorphismCard(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Progresso do Módulo',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: LearningPathColors.textPrimary,
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: isCompleted
                      ? LearningPathColors.successGreen.withOpacity(0.1)
                      : isCurrentModule
                          ? LearningPathColors.primaryPurple.withOpacity(0.1)
                          : LearningPathColors.progressLocked.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isCompleted
                        ? LearningPathColors.successGreen.withOpacity(0.3)
                        : isCurrentModule
                            ? LearningPathColors.primaryPurple.withOpacity(0.3)
                            : LearningPathColors.progressLocked
                                .withOpacity(0.3),
                  ),
                ),
                child: Text(
                  isCompleted
                      ? 'Concluído'
                      : isCurrentModule
                          ? 'Em andamento'
                          : 'Bloqueado',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isCompleted
                        ? LearningPathColors.successGreen
                        : isCurrentModule
                            ? LearningPathColors.primaryPurple
                            : LearningPathColors.progressLocked,
                  ),
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
              widthFactor: completedMissions / widget.module.missions.length,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  gradient: LinearGradient(
                    colors: isCompleted
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
          const SizedBox(height: 12),
          Text(
            '$completedMissions de ${widget.module.missions.length} missões concluídas',
            style: TextStyle(
              fontSize: 14,
              color: LearningPathColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMissionsList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'Missões',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: LearningPathColors.textPrimary,
            ),
          ),
        ),
        ...widget.module.missions.map((mission) {
          final isCompleted =
              widget.progress?.completedMissions.contains(mission.id) ?? false;
          final isLocked = !isCompleted && !_isMissionAvailable(mission);

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: MissionListItem(
              mission: mission,
              progress: widget.progress,
              isLocked: isLocked,
              onTap: () => _navigateToMission(mission),
            ),
          );
        }).toList(),
        const SizedBox(height: 20),
      ],
    );
  }

  bool _isMissionAvailable(MissionReference mission) {
    // Verifica se a missão está disponível baseada na ordem
    final missionIndex = widget.module.missions.indexOf(mission);

    // Se é a primeira missão, está sempre disponível se o módulo estiver ativo
    if (missionIndex == 0) {
      return true;
    }

    // Para outras missões, verifica se a anterior foi concluída
    final previousMission = widget.module.missions[missionIndex - 1];
    return widget.progress?.completedMissions.contains(previousMission.id) ??
        false;
  }

  void _navigateToMission(MissionReference mission) {
    // Navega para o quiz real usando o sistema existente
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QuizPage(
          missionId: mission.id,
          quizId: mission.missionId, // Usando o missionId real do quiz
          missionTitle: 'Missão ${mission.order} - ${widget.module.name}',
          pathId: widget.pathId, // Passa o ID da trilha
          isLearningPathMission: true, // Marca como missão de trilha
        ),
      ),
    ).then((result) {
      // O QuizPage já lida com a conclusão da missão
      // Aqui podemos apenas atualizar a UI se necessário
      if (result != null && result is Map<String, dynamic>) {
        setState(() {
          // Força atualização da UI para mostrar missão como concluída
        });
      }
    });
  }
}
