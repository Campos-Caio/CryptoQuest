import 'package:flutter/material.dart';
import 'package:cryptoquest/features/feedback/models/feedback_event.dart';
import 'package:cryptoquest/features/feedback/models/feedback_sequence.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/features/feedback/services/feedback_analyzer.dart';
import 'package:cryptoquest/features/feedback/services/feedback_sequencer.dart';

/// Serviço central de feedback
///
/// Ponto único de entrada para todo o sistema de feedback.
/// Analisa contexto, gera sequências e executa eventos de feedback.
class FeedbackService {
  /// Exibe feedback para quiz
  static Future<void> showQuizFeedback({
    required BuildContext context,
    required Map<String, dynamic> quizResult,
    required RewardFeedbackModel rewardData,
    VoidCallback? onComplete,
    VoidCallback? onCancel,
  }) {
    final sequence = FeedbackAnalyzer.analyzeQuizContext(
      contextData: quizResult,
      rewardData: rewardData,
    );

    return _executeFeedbackSequence(
      context: context,
      sequence: sequence,
      onComplete: onComplete,
      onCancel: onCancel,
    );
  }

  /// Exibe feedback para missão
  static Future<void> showMissionFeedback({
    required BuildContext context,
    required Map<String, dynamic> missionResult,
    required RewardFeedbackModel rewardData,
    VoidCallback? onComplete,
    VoidCallback? onCancel,
  }) {
    final sequence = FeedbackAnalyzer.analyzeMissionContext(
      contextData: missionResult,
      rewardData: rewardData,
    );

    return _executeFeedbackSequence(
      context: context,
      sequence: sequence,
      onComplete: onComplete,
      onCancel: onCancel,
    );
  }

  /// Exibe feedback para trilha de aprendizado
  static Future<void> showLearningPathFeedback({
    required BuildContext context,
    required Map<String, dynamic> pathResult,
    required RewardFeedbackModel rewardData,
    VoidCallback? onComplete,
    VoidCallback? onCancel,
  }) {
    final sequence = FeedbackAnalyzer.analyzeLearningPathContext(
      contextData: pathResult,
      rewardData: rewardData,
    );

    return _executeFeedbackSequence(
      context: context,
      sequence: sequence,
      onComplete: onComplete,
      onCancel: onCancel,
    );
  }

  /// Exibe feedback genérico baseado no contexto
  static Future<void> showGenericFeedback({
    required BuildContext context,
    required String actionType,
    required Map<String, dynamic> contextData,
    required RewardFeedbackModel rewardData,
    VoidCallback? onComplete,
    VoidCallback? onCancel,
  }) {
    final sequence = FeedbackAnalyzer.analyzeContext(
      actionType: actionType,
      contextData: contextData,
      rewardData: rewardData,
    );

    return _executeFeedbackSequence(
      context: context,
      sequence: sequence,
      onComplete: onComplete,
      onCancel: onCancel,
    );
  }

  /// Exibe feedback customizado com sequência específica
  static Future<void> showCustomFeedback({
    required BuildContext context,
    required FeedbackSequence sequence,
    VoidCallback? onComplete,
    VoidCallback? onCancel,
  }) {
    return _executeFeedbackSequence(
      context: context,
      sequence: sequence,
      onComplete: onComplete,
      onCancel: onCancel,
    );
  }

  /// Exibe feedback rápido via SnackBar
  static void showQuickFeedback({
    required BuildContext context,
    required String message,
    int? xpGained,
    int? pointsGained,
    IconData icon = Icons.check_circle,
    Color? color,
    Duration duration = const Duration(seconds: 3),
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
        duration: duration,
      ),
    );
  }

  /// Exibe notificação de badge conquistado
  static void showBadgeNotification({
    required BuildContext context,
    required BadgeData badge,
    VoidCallback? onTap,
    Duration duration = const Duration(seconds: 4),
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
        duration: duration,
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

  /// Executa uma sequência de feedback
  static Future<void> _executeFeedbackSequence({
    required BuildContext context,
    required FeedbackSequence sequence,
    VoidCallback? onComplete,
    VoidCallback? onCancel,
  }) {
    if (sequence.isEmpty) {
      onComplete?.call();
      return Future.value();
    }

    return FeedbackSequencer.executeSequence(
      context: context,
      sequence: sequence,
      onSequenceComplete: onComplete,
      onSequenceCancelled: onCancel,
    );
  }

  /// Cancela todas as sequências de feedback ativas
  static void cancelAllFeedback() {
    FeedbackSequencer.cancelAllSequences();
  }

  /// Retorna se há feedback ativo
  static bool get hasActiveFeedback => FeedbackSequencer.hasActiveSequences;

  /// Retorna o número de sequências ativas
  static int get activeFeedbackCount => FeedbackSequencer.activeSequenceCount;

  /// Cria dados de recompensa a partir de resultado de API
  static RewardFeedbackModel createRewardDataFromApiResponse({
    required Map<String, dynamic> apiResponse,
    required int previousXP,
    required int currentXP,
    required int previousLevel,
    required int currentLevel,
    int streakDays = 0,
    double quizPercentage = 0.0,
    bool isSuccess = true,
    String? message,
  }) {
    return RewardFeedbackModel(
      xpGained: apiResponse['xp_gained'] ?? 0,
      pointsGained: apiResponse['points_gained'] ?? 0,
      previousXP: previousXP,
      currentXP: currentXP,
      previousLevel: previousLevel,
      currentLevel: currentLevel,
      leveledUp: currentLevel > previousLevel,
      badgesEarned: (apiResponse['badges_earned'] as List<dynamic>?)
              ?.map((badge) => BadgeData.fromJson(badge))
              .toList() ??
          [],
      streakDays: streakDays,
      quizPercentage: quizPercentage,
      isSuccess: isSuccess,
      message: message,
    );
  }

  /// Cria dados de recompensa para quiz
  static RewardFeedbackModel createQuizRewardData({
    required double percentage,
    required int xpGained,
    required int pointsGained,
    required int previousXP,
    required int currentXP,
    required int previousLevel,
    required int currentLevel,
    int streakDays = 0,
    List<BadgeData> badgesEarned = const [],
  }) {
    return RewardFeedbackModel(
      xpGained: xpGained,
      pointsGained: pointsGained,
      previousXP: previousXP,
      currentXP: currentXP,
      previousLevel: previousLevel,
      currentLevel: currentLevel,
      leveledUp: currentLevel > previousLevel,
      badgesEarned: badgesEarned,
      streakDays: streakDays,
      quizPercentage: percentage,
      isSuccess: percentage >= 70,
      message: _generateQuizMessage(percentage),
    );
  }

  /// Cria dados de recompensa para missão
  static RewardFeedbackModel createMissionRewardData({
    required bool isSuccess,
    required int xpGained,
    required int pointsGained,
    required int previousXP,
    required int currentXP,
    required int previousLevel,
    required int currentLevel,
    int streakDays = 0,
    List<BadgeData> badgesEarned = const [],
    String? message,
  }) {
    return RewardFeedbackModel(
      xpGained: xpGained,
      pointsGained: pointsGained,
      previousXP: previousXP,
      currentXP: currentXP,
      previousLevel: previousLevel,
      currentLevel: currentLevel,
      leveledUp: currentLevel > previousLevel,
      badgesEarned: badgesEarned,
      streakDays: streakDays,
      quizPercentage: 0.0,
      isSuccess: isSuccess,
      message: message ??
          (isSuccess
              ? 'Missão completada com sucesso!'
              : 'Missão não concluída.'),
    );
  }

  /// Gera mensagem para quiz baseada na performance
  static String _generateQuizMessage(double percentage) {
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
}
