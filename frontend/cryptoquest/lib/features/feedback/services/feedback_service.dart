import 'package:flutter/material.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/features/feedback/widgets/reward_summary_sheet.dart';

/// Serviço para gerenciar exibição de feedback visual
///
/// Centraliza a lógica de quando e como exibir feedback
/// ao usuário, simplificando o uso em diferentes partes do app
class FeedbackService {
  /// Exibe feedback após completar missão
  static Future<void> showMissionCompleteFeedback({
    required BuildContext context,
    required Map<String, dynamic> missionResult,
    required int previousXP,
    required int currentXP,
    required int previousLevel,
    required int currentLevel,
    required int streakDays,
    double? quizPercentage,
    List<BadgeData>? badges,
    VoidCallback? onContinue,
  }) {
    final rewardData = RewardFeedbackModel(
      xpGained: missionResult['xp'] ?? missionResult['points'] ?? 0,
      pointsGained: missionResult['points'] ?? 0,
      previousXP: previousXP,
      currentXP: currentXP,
      previousLevel: previousLevel,
      currentLevel: currentLevel,
      leveledUp: currentLevel > previousLevel,
      badgesEarned: badges ?? [],
      streakDays: streakDays,
      quizPercentage: quizPercentage ?? 0.0,
      isSuccess: quizPercentage == null || quizPercentage >= 70,
      message: _generateMessage(quizPercentage),
    );

    return RewardSummarySheet.show(
      context: context,
      rewardData: rewardData,
      onContinue: onContinue,
      onViewProfile: () {
        Navigator.pushNamed(context, '/profile');
      },
      onViewBadges: badges != null && badges.isNotEmpty
          ? () {
              Navigator.pushNamed(context, '/rewards');
            }
          : null,
    );
  }

  /// Exibe feedback rápido via SnackBar
  ///
  /// Usado para conquistas menores que não justificam
  /// um bottom sheet completo
  static void showQuickFeedback({
    required BuildContext context,
    required String message,
    int? xpGained,
    int? pointsGained,
    IconData icon = Icons.check_circle,
    Color? color,
  }) {
    final displayColor = color ?? Colors.green;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(icon, color: displayColor),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    message,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  if (xpGained != null || pointsGained != null)
                    Text(
                      '${xpGained != null ? '+$xpGained XP' : ''}'
                      '${xpGained != null && pointsGained != null ? ' • ' : ''}'
                      '${pointsGained != null ? '+$pointsGained pts' : ''}',
                      style: const TextStyle(fontSize: 12),
                    ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: displayColor.withOpacity(0.9),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.all(16),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  /// Exibe notificação de badge conquistado
  ///
  /// Exibição rápida e não intrusiva de badge conquistado
  static void showBadgeNotification({
    required BuildContext context,
    required BadgeData badge,
    VoidCallback? onTap,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Text(
              badge.icon,
              style: const TextStyle(fontSize: 32),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Novo Badge!',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    badge.name,
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: Color(
          int.parse(badge.rarityColor.replaceFirst('#', '0xFF')),
        ).withOpacity(0.9),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.all(16),
        duration: const Duration(seconds: 4),
        action: onTap != null
            ? SnackBarAction(
                label: 'Ver',
                textColor: Colors.white,
                onPressed: onTap,
              )
            : null,
      ),
    );
  }

  /// Gera mensagem motivacional baseada no resultado
  static String _generateMessage(double? percentage) {
    if (percentage == null) {
      return 'Missão completada com sucesso!';
    }

    if (percentage >= 90) {
      return 'Desempenho excepcional! Você é incrível!';
    } else if (percentage >= 80) {
      return 'Ótimo trabalho! Continue assim!';
    } else if (percentage >= 70) {
      return 'Bom trabalho! Você está progredindo!';
    } else if (percentage >= 50) {
      return 'Não desista! Revise o conteúdo e tente novamente.';
    } else {
      return 'Continue estudando! A prática leva à perfeição.';
    }
  }

  /// Determina se deve mostrar confetti baseado nas recompensas
  static bool shouldShowConfetti(RewardFeedbackModel rewardData) {
    return rewardData.celebrationType == CelebrationType.major ||
        rewardData.celebrationType == CelebrationType.levelUp ||
        rewardData.celebrationType == CelebrationType.legendary ||
        rewardData.celebrationType == CelebrationType.multiple;
  }
}
