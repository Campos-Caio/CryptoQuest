import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';

/// Representa um evento individual de feedback
///
/// Cada evento contém os dados necessários para exibir
/// uma tela específica de feedback com timing personalizado
class FeedbackEvent {
  final FeedbackType type;
  final RewardFeedbackModel data;
  final Duration delay;
  final bool shouldWaitForPrevious;
  final List<FeedbackAction> actions;
  final Map<String, dynamic>? customData;

  const FeedbackEvent({
    required this.type,
    required this.data,
    this.delay = Duration.zero,
    this.shouldWaitForPrevious = false,
    this.actions = const [],
    this.customData,
  });

  /// Cria evento de Level Up
  factory FeedbackEvent.levelUp({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.levelUp,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
      ],
    );
  }

  /// Cria evento de Badge Unlock
  factory FeedbackEvent.badgeUnlock({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.badgeUnlock,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
        FeedbackAction.viewBadges,
      ],
    );
  }

  /// Cria evento de Quiz Success
  factory FeedbackEvent.quizSuccess({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.quizSuccess,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
      ],
    );
  }

  /// Cria evento de Quiz Failure
  factory FeedbackEvent.quizFailure({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.quizFailure,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.retry,
        FeedbackAction.goHome,
        FeedbackAction.viewProfile,
      ],
    );
  }

  /// Cria evento de Streak Celebration
  factory FeedbackEvent.streakCelebration({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.streakCelebration,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
      ],
    );
  }

  /// Cria evento de Legendary Achievement
  factory FeedbackEvent.legendaryAchievement({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.legendaryAchievement,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
        FeedbackAction.viewBadges,
      ],
    );
  }

  /// Cria evento de Minor Achievement
  factory FeedbackEvent.minorAchievement({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.minorAchievement,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
      ],
    );
  }

  /// Cria evento de Mission Complete
  factory FeedbackEvent.missionComplete({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.missionComplete,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
      ],
    );
  }

  /// Cria evento de Learning Path Complete
  factory FeedbackEvent.learningPathComplete({
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
  }) {
    return FeedbackEvent(
      type: FeedbackType.learningPathComplete,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: [
        FeedbackAction.continueAction,
        FeedbackAction.viewProfile,
        FeedbackAction.viewLearningPaths,
      ],
    );
  }

  /// Cria evento customizado
  factory FeedbackEvent.custom({
    required FeedbackType type,
    required RewardFeedbackModel data,
    Duration delay = Duration.zero,
    bool shouldWaitForPrevious = false,
    List<FeedbackAction> actions = const [],
    Map<String, dynamic>? customData,
  }) {
    return FeedbackEvent(
      type: type,
      data: data,
      delay: delay,
      shouldWaitForPrevious: shouldWaitForPrevious,
      actions: actions,
      customData: customData,
    );
  }

  /// Retorna se o evento deve aguardar o anterior
  bool get shouldWait => shouldWaitForPrevious;

  /// Retorna se o evento tem ações disponíveis
  bool get hasActions => actions.isNotEmpty;

  /// Retorna se o evento é de sucesso
  bool get isSuccess => data.isSuccess;

  /// Retorna se o evento é de falha
  bool get isFailure => !data.isSuccess;
}

/// Tipos de eventos de feedback
enum FeedbackType {
  // Conquistas positivas
  levelUp,
  badgeUnlock,
  quizSuccess,
  streakCelebration,
  legendaryAchievement,
  minorAchievement,
  missionComplete,
  learningPathComplete,

  // Falhas e erros
  quizFailure,
  missionFailure,
  learningPathFailure,

  // Eventos especiais
  custom,
}

/// Ações disponíveis nos eventos de feedback
enum FeedbackAction {
  continueAction,
  retry,
  goHome,
  viewProfile,
  viewBadges,
  viewLearningPaths,
  viewMissions,
  custom,
}

/// Extensão para obter informações sobre tipos de feedback
extension FeedbackTypeExtension on FeedbackType {
  /// Retorna se o tipo é de sucesso
  bool get isSuccess {
    switch (this) {
      case FeedbackType.levelUp:
      case FeedbackType.badgeUnlock:
      case FeedbackType.quizSuccess:
      case FeedbackType.streakCelebration:
      case FeedbackType.legendaryAchievement:
      case FeedbackType.minorAchievement:
      case FeedbackType.missionComplete:
      case FeedbackType.learningPathComplete:
        return true;
      case FeedbackType.quizFailure:
      case FeedbackType.missionFailure:
      case FeedbackType.learningPathFailure:
        return false;
      case FeedbackType.custom:
        return true; // Assumir sucesso para custom
    }
  }

  /// Retorna se o tipo é de falha
  bool get isFailure => !isSuccess;

  /// Retorna se o tipo deve mostrar confetti
  bool get shouldShowConfetti {
    switch (this) {
      case FeedbackType.levelUp:
      case FeedbackType.legendaryAchievement:
      case FeedbackType.streakCelebration:
        return true;
      case FeedbackType.badgeUnlock:
      case FeedbackType.quizSuccess:
      case FeedbackType.missionComplete:
      case FeedbackType.learningPathComplete:
        return data?.celebrationType == CelebrationType.major ||
            data?.celebrationType == CelebrationType.multiple;
      case FeedbackType.minorAchievement:
        return false;
      case FeedbackType.quizFailure:
      case FeedbackType.missionFailure:
      case FeedbackType.learningPathFailure:
        return false;
      case FeedbackType.custom:
        return false;
    }
  }

  /// Retorna a duração da animação
  Duration get animationDuration {
    switch (this) {
      case FeedbackType.legendaryAchievement:
        return const Duration(milliseconds: 3000);
      case FeedbackType.levelUp:
        return const Duration(milliseconds: 2500);
      case FeedbackType.badgeUnlock:
      case FeedbackType.streakCelebration:
        return const Duration(milliseconds: 2000);
      case FeedbackType.quizSuccess:
      case FeedbackType.missionComplete:
      case FeedbackType.learningPathComplete:
        return const Duration(milliseconds: 1500);
      case FeedbackType.minorAchievement:
        return const Duration(milliseconds: 1000);
      case FeedbackType.quizFailure:
      case FeedbackType.missionFailure:
      case FeedbackType.learningPathFailure:
        return const Duration(milliseconds: 800);
      case FeedbackType.custom:
        return const Duration(milliseconds: 1000);
    }
  }

  /// Dados do evento (será definido quando necessário)
  RewardFeedbackModel? get data => null;
}
