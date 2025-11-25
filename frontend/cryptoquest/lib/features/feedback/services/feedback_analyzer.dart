import 'package:cryptoquest/features/feedback/models/feedback_event.dart';
import 'package:cryptoquest/features/feedback/models/feedback_sequence.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';

/// Analisador de contexto para determinar eventos de feedback
///
/// Analisa dados de contexto e determina quais eventos de feedback
/// devem ser exibidos e em que ordem
class FeedbackAnalyzer {
  /// Analisa contexto de quiz e retorna sequência de feedback
  static FeedbackSequence analyzeQuizContext({
    required Map<String, dynamic> contextData,
    required RewardFeedbackModel rewardData,
  }) {
    final events = <FeedbackEvent>[];

    // 1. Determinar evento principal baseado no resultado
    final percentage = rewardData.quizPercentage;
    final isSuccess = percentage >= 70;

    if (isSuccess) {
      // Quiz bem-sucedido
      events.add(FeedbackEvent.quizSuccess(
        data: rewardData,
        delay: Duration.zero,
      ));

      // 2. Verificar conquistas adicionais
      if (rewardData.leveledUp) {
        events.add(FeedbackEvent.levelUp(
          data: rewardData,
          delay: const Duration(milliseconds: 1500),
          shouldWaitForPrevious: true,
        ));
      }

      if (rewardData.badgesEarned.isNotEmpty) {
        events.add(FeedbackEvent.badgeUnlock(
          data: rewardData,
          delay: const Duration(milliseconds: 1000),
          shouldWaitForPrevious: true,
        ));
      }

      if (rewardData.streakDays >= 7) {
        events.add(FeedbackEvent.streakCelebration(
          data: rewardData,
          delay: const Duration(milliseconds: 1000),
          shouldWaitForPrevious: true,
        ));
      }

      // 3. Verificar conquista lendária
      if (rewardData.celebrationType == CelebrationType.legendary) {
        events.add(FeedbackEvent.legendaryAchievement(
          data: rewardData,
          delay: const Duration(milliseconds: 500),
          shouldWaitForPrevious: true,
        ));
      }
    } else {
      // Quiz falhou - passar contexto para acesso ao callback de retry
      events.add(FeedbackEvent(
        type: FeedbackType.quizFailure,
        data: rewardData,
        delay: Duration.zero,
        actions: [
          FeedbackAction.retry,
          FeedbackAction.continueAction,
        ],
        customData: contextData,
      ));
    }

    return events.isEmpty
        ? FeedbackSequence.empty()
        : FeedbackSequence.multiple(events);
  }

  /// Analisa contexto de missão e retorna sequência de feedback
  static FeedbackSequence analyzeMissionContext({
    required Map<String, dynamic> contextData,
    required RewardFeedbackModel rewardData,
  }) {
    final events = <FeedbackEvent>[];

    // 1. Determinar se a missão foi bem-sucedida
    final isSuccess = rewardData.isSuccess;

    if (isSuccess) {
      // Missão bem-sucedida
      events.add(FeedbackEvent.missionComplete(
        data: rewardData,
        delay: Duration.zero,
      ));

      // 2. Verificar conquistas adicionais
      if (rewardData.leveledUp) {
        events.add(FeedbackEvent.levelUp(
          data: rewardData,
          delay: const Duration(milliseconds: 1500),
          shouldWaitForPrevious: true,
        ));
      }

      if (rewardData.badgesEarned.isNotEmpty) {
        events.add(FeedbackEvent.badgeUnlock(
          data: rewardData,
          delay: const Duration(milliseconds: 1000),
          shouldWaitForPrevious: true,
        ));
      }

      if (rewardData.streakDays >= 7) {
        events.add(FeedbackEvent.streakCelebration(
          data: rewardData,
          delay: const Duration(milliseconds: 1000),
          shouldWaitForPrevious: true,
        ));
      }
    } else {
      // Missão falhou
      events.add(FeedbackEvent.custom(
        type: FeedbackType.missionFailure,
        data: rewardData,
        delay: Duration.zero,
      ));
    }

    return events.isEmpty
        ? FeedbackSequence.empty()
        : FeedbackSequence.multiple(events);
  }

  /// Analisa contexto de trilha de aprendizado e retorna sequência de feedback
  static FeedbackSequence analyzeLearningPathContext({
    required Map<String, dynamic> contextData,
    required RewardFeedbackModel rewardData,
  }) {
    final events = <FeedbackEvent>[];

    // 1. Determinar se a trilha foi completada
    final isSuccess = rewardData.isSuccess;

    if (isSuccess) {
      // Trilha completada
      events.add(FeedbackEvent.learningPathComplete(
        data: rewardData,
        delay: Duration.zero,
      ));

      // 2. Verificar conquistas adicionais
      if (rewardData.leveledUp) {
        events.add(FeedbackEvent.levelUp(
          data: rewardData,
          delay: const Duration(milliseconds: 2000),
          shouldWaitForPrevious: true,
        ));
      }

      if (rewardData.badgesEarned.isNotEmpty) {
        events.add(FeedbackEvent.badgeUnlock(
          data: rewardData,
          delay: const Duration(milliseconds: 1500),
          shouldWaitForPrevious: true,
        ));
      }

      if (rewardData.streakDays >= 7) {
        events.add(FeedbackEvent.streakCelebration(
          data: rewardData,
          delay: const Duration(milliseconds: 1000),
          shouldWaitForPrevious: true,
        ));
      }
    } else {
      // Trilha falhou
      events.add(FeedbackEvent.custom(
        type: FeedbackType.learningPathFailure,
        data: rewardData,
        delay: Duration.zero,
      ));
    }

    return events.isEmpty
        ? FeedbackSequence.empty()
        : FeedbackSequence.multiple(events);
  }

  /// Analisa contexto genérico e retorna sequência de feedback
  static FeedbackSequence analyzeGenericContext({
    required Map<String, dynamic> contextData,
    required RewardFeedbackModel rewardData,
  }) {
    final events = <FeedbackEvent>[];

    // 1. Determinar tipo de conquista baseado no celebration type
    switch (rewardData.celebrationType) {
      case CelebrationType.levelUp:
        events.add(FeedbackEvent.levelUp(
          data: rewardData,
          delay: Duration.zero,
        ));
        break;

      case CelebrationType.legendary:
        events.add(FeedbackEvent.legendaryAchievement(
          data: rewardData,
          delay: Duration.zero,
        ));
        break;

      case CelebrationType.badge:
      case CelebrationType.multiple:
        events.add(FeedbackEvent.badgeUnlock(
          data: rewardData,
          delay: Duration.zero,
        ));
        break;

      case CelebrationType.major:
        if (rewardData.quizPercentage > 0) {
          events.add(FeedbackEvent.quizSuccess(
            data: rewardData,
            delay: Duration.zero,
          ));
        } else {
          events.add(FeedbackEvent.missionComplete(
            data: rewardData,
            delay: Duration.zero,
          ));
        }
        break;

      case CelebrationType.minor:
        events.add(FeedbackEvent.minorAchievement(
          data: rewardData,
          delay: Duration.zero,
        ));
        break;

      case CelebrationType.none:
        // Sem conquistas significativas
        if (rewardData.isSuccess) {
          events.add(FeedbackEvent.minorAchievement(
            data: rewardData,
            delay: Duration.zero,
          ));
        }
        break;
    }

    return events.isEmpty
        ? FeedbackSequence.empty()
        : FeedbackSequence.multiple(events);
  }

  /// Analisa contexto baseado no tipo de ação
  static FeedbackSequence analyzeContext({
    required String actionType,
    required Map<String, dynamic> contextData,
    required RewardFeedbackModel rewardData,
  }) {
    switch (actionType.toLowerCase()) {
      case 'quiz':
        return analyzeQuizContext(
          contextData: contextData,
          rewardData: rewardData,
        );

      case 'mission':
        return analyzeMissionContext(
          contextData: contextData,
          rewardData: rewardData,
        );

      case 'learning_path':
      case 'learningpath':
        return analyzeLearningPathContext(
          contextData: contextData,
          rewardData: rewardData,
        );

      default:
        return analyzeGenericContext(
          contextData: contextData,
          rewardData: rewardData,
        );
    }
  }

  /// Determina se deve mostrar confetti baseado na sequência
  static bool shouldShowConfetti(FeedbackSequence sequence) {
    return sequence.confettiEvents.isNotEmpty;
  }

  /// Determina a duração total da sequência
  static Duration calculateTotalDuration(FeedbackSequence sequence) {
    return sequence.totalDuration;
  }

  /// Determina se a sequência deve mostrar progresso
  static bool shouldShowProgress(FeedbackSequence sequence) {
    return sequence.isMultiple && sequence.totalDuration.inSeconds > 3;
  }

  /// Gera título para a sequência
  static String generateSequenceTitle(FeedbackSequence sequence) {
    if (sequence.isEmpty) return '';

    if (sequence.isSingle) {
      final event = sequence.firstEvent!;
      switch (event.type) {
        case FeedbackType.levelUp:
          return 'Level Up!';
        case FeedbackType.badgeUnlock:
          return 'Badge Desbloqueado!';
        case FeedbackType.quizSuccess:
          return 'Quiz Concluído!';
        case FeedbackType.quizFailure:
          return 'Tente Novamente';
        case FeedbackType.streakCelebration:
          return 'Sequência Ativa!';
        case FeedbackType.legendaryAchievement:
          return 'Conquista Lendária!';
        case FeedbackType.minorAchievement:
          return 'Conquista!';
        case FeedbackType.missionComplete:
          return 'Missão Concluída!';
        case FeedbackType.learningPathComplete:
          return 'Trilha Concluída!';
        case FeedbackType.missionFailure:
        case FeedbackType.learningPathFailure:
          return 'Continue Tentando';
        case FeedbackType.custom:
          return 'Evento Especial';
      }
    }

    if (sequence.isAllSuccess) {
      return 'Múltiplas Conquistas!';
    } else if (sequence.isAllFailure) {
      return 'Continue Tentando';
    } else {
      return 'Resultado Misto';
    }
  }
}
