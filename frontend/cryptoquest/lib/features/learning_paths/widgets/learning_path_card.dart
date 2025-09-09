import 'package:flutter/material.dart';
import '../models/learning_path_model.dart';
import '../models/user_path_progress_model.dart';
import '../theme/learning_path_colors.dart';
import 'glassmorphism_card.dart';

class LearningPathCard extends StatelessWidget {
  final LearningPath learningPath;
  final UserPathProgress? progress;
  final VoidCallback? onTap;
  final bool showProgress;

  const LearningPathCard({
    Key? key,
    required this.learningPath,
    this.progress,
    this.onTap,
    this.showProgress = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isCompleted = progress?.completedAt != null;
    final isStarted = progress != null;

    return GlassmorphismCard(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      onTap: onTap,
      isElevated: isStarted,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header com título e dificuldade
          Row(
            children: [
              Expanded(
                child: Text(
                  learningPath.name,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: LearningPathColors.textPrimary,
                  ),
                ),
              ),
              _buildDifficultyChip(),
            ],
          ),

          const SizedBox(height: 8),

          // Descrição
          Text(
            learningPath.description,
            style: TextStyle(
              fontSize: 14,
              color: LearningPathColors.textSecondary,
              height: 1.4,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),

          const SizedBox(height: 16),

          // Informações da trilha
          Row(
            children: [
              Icon(
                Icons.schedule,
                size: 16,
                color: LearningPathColors.textTertiary,
              ),
              const SizedBox(width: 4),
              Text(
                learningPath.estimatedDuration,
                style: TextStyle(
                  fontSize: 12,
                  color: LearningPathColors.textTertiary,
                ),
              ),
              const SizedBox(width: 16),
              Icon(
                Icons.layers,
                size: 16,
                color: LearningPathColors.textTertiary,
              ),
              const SizedBox(width: 4),
              Text(
                '${learningPath.modules.length} módulos',
                style: TextStyle(
                  fontSize: 12,
                  color: LearningPathColors.textTertiary,
                ),
              ),
            ],
          ),

          // Progresso (se disponível)
          if (showProgress && progress != null) ...[
            const SizedBox(height: 16),
            _buildProgressBar(),
          ],

          // Status da trilha
          if (showProgress) ...[
            const SizedBox(height: 12),
            _buildStatusIndicator(),
          ],
        ],
      ),
    );
  }

  Widget _buildDifficultyChip() {
    final chipColor =
        LearningPathColors.getDifficultyColor(learningPath.difficulty);
    final difficultyText =
        LearningPathColors.getDifficultyText(learningPath.difficulty);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            chipColor.withOpacity(0.2),
            chipColor.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: chipColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        difficultyText,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: chipColor,
        ),
      ),
    );
  }

  Widget _buildProgressBar() {
    final percentage = progress?.progressPercentage ?? 0.0;
    final isCompleted = percentage == 100;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Progresso',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: LearningPathColors.textSecondary,
              ),
            ),
            Text(
              '${percentage.toStringAsFixed(1)}%',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: isCompleted
                    ? LearningPathColors.successGreen
                    : LearningPathColors.primaryPurple,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 6,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(3),
            color: LearningPathColors.progressBackground,
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: percentage / 100,
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(3),
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
      ],
    );
  }

  Widget _buildStatusIndicator() {
    if (progress == null) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: LearningPathColors.primaryPurple.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: LearningPathColors.primaryPurple.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.play_circle_outline,
              size: 16,
              color: LearningPathColors.primaryPurple,
            ),
            const SizedBox(width: 6),
            Text(
              'Não iniciada',
              style: TextStyle(
                fontSize: 12,
                color: LearningPathColors.primaryPurple,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
    }

    if (progress!.completedAt != null) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: LearningPathColors.successGreen.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: LearningPathColors.successGreen.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.check_circle,
              size: 16,
              color: LearningPathColors.successGreen,
            ),
            const SizedBox(width: 6),
            Text(
              'Concluída',
              style: TextStyle(
                fontSize: 12,
                color: LearningPathColors.successGreen,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: LearningPathColors.warningOrange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: LearningPathColors.warningOrange.withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.play_circle_filled,
            size: 16,
            color: LearningPathColors.warningOrange,
          ),
          const SizedBox(width: 6),
          Text(
            'Em andamento',
            style: TextStyle(
              fontSize: 12,
              color: LearningPathColors.warningOrange,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
