import 'package:flutter/material.dart';
import '../models/learning_path_model.dart';
import '../models/user_path_progress_model.dart';
import '../theme/learning_path_colors.dart';
import 'glassmorphism_card.dart';

class ModuleCard extends StatelessWidget {
  final Module module;
  final UserPathProgress? progress;
  final VoidCallback? onTap;
  final bool isCurrentModule;

  const ModuleCard({
    Key? key,
    required this.module,
    this.progress,
    this.onTap,
    this.isCurrentModule = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isCompleted = progress?.completedModules.contains(module.id) ?? false;
    final isLocked = !isCompleted && !isCurrentModule && progress != null;

    return GlassmorphismCard(
      margin: const EdgeInsets.symmetric(horizontal: 0, vertical: 6),
      onTap: isLocked ? null : onTap,
      isElevated: isCurrentModule,
      backgroundColor: isLocked
          ? LearningPathColors.progressLocked.withOpacity(0.1)
          : isCompleted
              ? LearningPathColors.successGreen.withOpacity(0.1)
              : isCurrentModule
                  ? LearningPathColors.primaryPurple.withOpacity(0.1)
                  : null,
      child: Row(
        children: [
          // Ícone do módulo
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors:
                    _getModuleGradient(isCompleted, isCurrentModule, isLocked),
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: _getModuleColor(isCompleted, isCurrentModule, isLocked)
                      .withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Icon(
              _getModuleIcon(isCompleted, isCurrentModule, isLocked),
              color: LearningPathColors.textPrimary,
              size: 28,
            ),
          ),

          const SizedBox(width: 16),

          // Conteúdo do módulo
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Título do módulo
                Text(
                  module.name,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isLocked
                        ? LearningPathColors.textTertiary
                        : LearningPathColors.textPrimary,
                  ),
                ),

                const SizedBox(height: 6),

                // Descrição
                Text(
                  module.description,
                  style: TextStyle(
                    fontSize: 14,
                    color: isLocked
                        ? LearningPathColors.textTertiary
                        : LearningPathColors.textSecondary,
                    height: 1.3,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),

                const SizedBox(height: 12),

                // Informações do módulo
                Row(
                  children: [
                    Icon(
                      Icons.quiz,
                      size: 16,
                      color: isLocked
                          ? LearningPathColors.textTertiary
                          : LearningPathColors.textTertiary,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      '${module.missions.length} missões',
                      style: TextStyle(
                        fontSize: 12,
                        color: isLocked
                            ? LearningPathColors.textTertiary
                            : LearningPathColors.textTertiary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(width: 20),
                    Icon(
                      Icons.sort,
                      size: 16,
                      color: isLocked
                          ? LearningPathColors.textTertiary
                          : LearningPathColors.textTertiary,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Módulo ${module.order}',
                      style: TextStyle(
                        fontSize: 12,
                        color: isLocked
                            ? LearningPathColors.textTertiary
                            : LearningPathColors.textTertiary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Indicador de status
          if (isCompleted)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: LearningPathColors.successGradient,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.check,
                color: LearningPathColors.textPrimary,
                size: 20,
              ),
            )
          else if (isCurrentModule)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: LearningPathColors.primaryGradient,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.play_arrow,
                color: LearningPathColors.textPrimary,
                size: 20,
              ),
            )
          else if (isLocked)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: LearningPathColors.progressLocked,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.lock,
                color: LearningPathColors.textPrimary,
                size: 20,
              ),
            ),
        ],
      ),
    );
  }

  Color _getModuleColor(bool isCompleted, bool isCurrentModule, bool isLocked) {
    if (isLocked) return LearningPathColors.progressLocked;
    if (isCompleted) return LearningPathColors.successGreen;
    if (isCurrentModule) return LearningPathColors.primaryPurple;
    return LearningPathColors.textTertiary;
  }

  List<Color> _getModuleGradient(
      bool isCompleted, bool isCurrentModule, bool isLocked) {
    if (isLocked)
      return [
        LearningPathColors.progressLocked,
        LearningPathColors.progressLocked.withOpacity(0.7)
      ];
    if (isCompleted)
      return [
        LearningPathColors.successGreen,
        LearningPathColors.successGreenLight
      ];
    if (isCurrentModule)
      return [
        LearningPathColors.primaryPurple,
        LearningPathColors.primaryPurpleLight
      ];
    return [
      LearningPathColors.textTertiary,
      LearningPathColors.textTertiary.withOpacity(0.7)
    ];
  }

  IconData _getModuleIcon(
      bool isCompleted, bool isCurrentModule, bool isLocked) {
    if (isLocked) return Icons.lock;
    if (isCompleted) return Icons.check_circle;
    if (isCurrentModule) return Icons.play_circle_filled;
    return Icons.circle_outlined;
  }
}
