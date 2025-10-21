import 'package:flutter/material.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/features/feedback/services/feedback_service.dart';

/// Factory para criar telas de feedback especializadas
///
/// DEPRECATED: Use FeedbackService diretamente para melhor funcionalidade
/// Este factory mantém compatibilidade com código existente
class FeedbackScreenFactory {
  /// Exibe a tela de feedback apropriada baseada no tipo de conquista
  ///
  /// DEPRECATED: Use FeedbackService.showGenericFeedback() em vez disso
  @Deprecated(
      'Use FeedbackService.showGenericFeedback() para melhor funcionalidade')
  static Future<void> showFeedback({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
    VoidCallback? onViewBadges,
  }) {
    // Usar o novo serviço central de feedback
    return FeedbackService.showGenericFeedback(
      context: context,
      actionType: 'generic',
      contextData: {},
      rewardData: rewardData,
      onComplete: onContinue,
    );
  }

  /// Determina se deve mostrar confetti baseado no tipo de celebração
  static bool shouldShowConfetti(CelebrationType type) {
    return type != CelebrationType.none && type != CelebrationType.minor;
  }

  /// Retorna a duração da animação baseada no tipo
  static Duration getAnimationDuration(CelebrationType type) {
    switch (type) {
      case CelebrationType.legendary:
        return const Duration(milliseconds: 3000);
      case CelebrationType.levelUp:
        return const Duration(milliseconds: 2500);
      case CelebrationType.major:
      case CelebrationType.multiple:
        return const Duration(milliseconds: 2000);
      case CelebrationType.badge:
        return const Duration(milliseconds: 1500);
      case CelebrationType.minor:
        return const Duration(milliseconds: 1000);
      case CelebrationType.none:
        return const Duration(milliseconds: 500);
    }
  }
}
