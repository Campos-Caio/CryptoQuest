import 'dart:async';
import 'package:flutter/material.dart';
import 'package:cryptoquest/features/feedback/models/feedback_event.dart';
import 'package:cryptoquest/features/feedback/models/feedback_sequence.dart';
import 'package:cryptoquest/features/feedback/screens/level_up_screen.dart';
import 'package:cryptoquest/features/feedback/screens/badge_unlock_screen.dart';
import 'package:cryptoquest/features/feedback/screens/quiz_results_screen.dart';
import 'package:cryptoquest/features/feedback/screens/streak_celebration_screen.dart';
import 'package:cryptoquest/features/feedback/screens/legendary_achievement_screen.dart';
import 'package:cryptoquest/features/feedback/screens/minor_achievement_screen.dart';

/// Sequenciador de eventos de feedback
///
/// Gerencia a exibição sequencial de eventos de feedback
/// com timing preciso e transições suaves
class FeedbackSequencer {
  static final Map<String, Completer<void>> _activeSequences = {};

  /// Executa uma sequência de eventos de feedback
  static Future<void> executeSequence({
    required BuildContext context,
    required FeedbackSequence sequence,
    VoidCallback? onSequenceComplete,
    VoidCallback? onSequenceCancelled,
  }) {
    if (sequence.isEmpty) {
      onSequenceComplete?.call();
      return Future.value();
    }

    final sequenceId = DateTime.now().millisecondsSinceEpoch.toString();
    final completer = Completer<void>();
    _activeSequences[sequenceId] = completer;

    _executeSequenceInternal(
      context: context,
      sequence: sequence,
      sequenceId: sequenceId,
      onSequenceComplete: onSequenceComplete,
      onSequenceCancelled: onSequenceCancelled,
    );

    return completer.future;
  }

  /// Executa a sequência internamente
  static Future<void> _executeSequenceInternal({
    required BuildContext context,
    required FeedbackSequence sequence,
    required String sequenceId,
    VoidCallback? onSequenceComplete,
    VoidCallback? onSequenceCancelled,
  }) async {
    try {
      for (int i = 0; i < sequence.events.length; i++) {
        final event = sequence.events[i];

        // Verificar se a sequência foi cancelada
        if (!_activeSequences.containsKey(sequenceId)) {
          onSequenceCancelled?.call();
          return;
        }

        // Aguardar delay do evento
        if (event.delay > Duration.zero) {
          await Future.delayed(event.delay);
        }

        // Verificar se deve aguardar o evento anterior
        if (event.shouldWaitForPrevious && i > 0) {
          // Aguardar um pouco mais para garantir que o anterior terminou
          await Future.delayed(const Duration(milliseconds: 500));
        }

        // Verificar se a sequência foi cancelada novamente
        if (!_activeSequences.containsKey(sequenceId)) {
          onSequenceCancelled?.call();
          return;
        }

        // Executar o evento
        await _executeEvent(context, event);

        // Aguardar a duração da animação do evento
        await Future.delayed(event.type.animationDuration);
      }

      // Sequência concluída com sucesso
      _activeSequences.remove(sequenceId);
      onSequenceComplete?.call();
    } catch (e) {
      // Erro durante a execução
      _activeSequences.remove(sequenceId);
      onSequenceCancelled?.call();
      rethrow;
    }
  }

  /// Executa um evento individual
  static Future<void> _executeEvent(BuildContext context, FeedbackEvent event) {
    switch (event.type) {
      case FeedbackType.levelUp:
        return LevelUpScreen.show(
          context: context,
          rewardData: event.data,
          onContinue: () =>
              _handleEventAction(context, event, FeedbackAction.continueAction),
          onViewProfile: () =>
              _handleEventAction(context, event, FeedbackAction.viewProfile),
        );

      case FeedbackType.badgeUnlock:
        return BadgeUnlockScreen.show(
          context: context,
          rewardData: event.data,
          onContinue: () =>
              _handleEventAction(context, event, FeedbackAction.continueAction),
          onViewProfile: () =>
              _handleEventAction(context, event, FeedbackAction.viewProfile),
          onViewBadges: () =>
              _handleEventAction(context, event, FeedbackAction.viewBadges),
        );

      case FeedbackType.quizSuccess:
        return QuizResultsScreen.show(
          context: context,
          rewardData: event.data,
          onContinue: () =>
              _handleEventAction(context, event, FeedbackAction.continueAction),
          onViewProfile: () =>
              _handleEventAction(context, event, FeedbackAction.viewProfile),
        );

      case FeedbackType.quizFailure:
        return _showQuizFailureScreen(
          context: context,
          event: event,
        );

      case FeedbackType.streakCelebration:
        return StreakCelebrationScreen.show(
          context: context,
          rewardData: event.data,
          onContinue: () =>
              _handleEventAction(context, event, FeedbackAction.continueAction),
          onViewProfile: () =>
              _handleEventAction(context, event, FeedbackAction.viewProfile),
        );

      case FeedbackType.legendaryAchievement:
        return LegendaryAchievementScreen.show(
          context: context,
          rewardData: event.data,
          onContinue: () =>
              _handleEventAction(context, event, FeedbackAction.continueAction),
          onViewProfile: () =>
              _handleEventAction(context, event, FeedbackAction.viewProfile),
          onViewBadges: () =>
              _handleEventAction(context, event, FeedbackAction.viewBadges),
        );

      case FeedbackType.minorAchievement:
        return MinorAchievementScreen.show(
          context: context,
          rewardData: event.data,
          onContinue: () =>
              _handleEventAction(context, event, FeedbackAction.continueAction),
        );

      case FeedbackType.missionComplete:
        return _showMissionCompleteScreen(
          context: context,
          event: event,
        );

      case FeedbackType.learningPathComplete:
        return _showLearningPathCompleteScreen(
          context: context,
          event: event,
        );

      case FeedbackType.missionFailure:
        return _showMissionFailureScreen(
          context: context,
          event: event,
        );

      case FeedbackType.learningPathFailure:
        return _showLearningPathFailureScreen(
          context: context,
          event: event,
        );

      case FeedbackType.custom:
        return _showCustomScreen(
          context: context,
          event: event,
        );
    }
  }

  /// Manipula ações dos eventos
  static void _handleEventAction(
      BuildContext context, FeedbackEvent event, FeedbackAction action) {
    switch (action) {
      case FeedbackAction.continueAction:
        Navigator.of(context).pop();
        break;
      case FeedbackAction.retry:
        Navigator.of(context).pop();
        // Implementar lógica de retry baseada no contexto
        break;
      case FeedbackAction.goHome:
        Navigator.of(context).pop();
        Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
        break;
      case FeedbackAction.viewProfile:
        Navigator.of(context).pop();
        Navigator.of(context).pushNamed('/profile');
        break;
      case FeedbackAction.viewBadges:
        Navigator.of(context).pop();
        Navigator.of(context).pushNamed('/rewards');
        break;
      case FeedbackAction.viewLearningPaths:
        Navigator.of(context).pop();
        Navigator.of(context).pushNamed('/learning-paths');
        break;
      case FeedbackAction.viewMissions:
        Navigator.of(context).pop();
        Navigator.of(context).pushNamed('/missions');
        break;
      case FeedbackAction.custom:
        // Implementar ação customizada baseada no evento
        Navigator.of(context).pop();
        break;
    }
  }

  /// Cancela uma sequência ativa
  static void cancelSequence(String sequenceId) {
    final completer = _activeSequences.remove(sequenceId);
    if (completer != null && !completer.isCompleted) {
      completer.complete();
    }
  }

  /// Cancela todas as sequências ativas
  static void cancelAllSequences() {
    for (final completer in _activeSequences.values) {
      if (!completer.isCompleted) {
        completer.complete();
      }
    }
    _activeSequences.clear();
  }

  /// Retorna se há sequências ativas
  static bool get hasActiveSequences => _activeSequences.isNotEmpty;

  /// Retorna o número de sequências ativas
  static int get activeSequenceCount => _activeSequences.length;

  // Métodos auxiliares para telas que ainda não existem

  /// Mostra tela de falha de quiz
  static Future<void> _showQuizFailureScreen({
    required BuildContext context,
    required FeedbackEvent event,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Quiz Não Aprovado'),
        content: Text(
            'Você acertou ${event.data.quizPercentage.toStringAsFixed(0)}% das questões. '
            'É necessário acertar pelo menos 70% para passar.'),
        actions: [
          TextButton(
            onPressed: () =>
                _handleEventAction(context, event, FeedbackAction.retry),
            child: const Text('Tentar Novamente'),
          ),
          TextButton(
            onPressed: () =>
                _handleEventAction(context, event, FeedbackAction.goHome),
            child: const Text('Voltar ao Início'),
          ),
        ],
      ),
    );
  }

  /// Mostra tela de missão completa
  static Future<void> _showMissionCompleteScreen({
    required BuildContext context,
    required FeedbackEvent event,
  }) {
    return MinorAchievementScreen.show(
      context: context,
      rewardData: event.data,
      onContinue: () =>
          _handleEventAction(context, event, FeedbackAction.continueAction),
    );
  }

  /// Mostra tela de trilha de aprendizado completa
  static Future<void> _showLearningPathCompleteScreen({
    required BuildContext context,
    required FeedbackEvent event,
  }) {
    return MinorAchievementScreen.show(
      context: context,
      rewardData: event.data,
      onContinue: () =>
          _handleEventAction(context, event, FeedbackAction.continueAction),
    );
  }

  /// Mostra tela de falha de missão
  static Future<void> _showMissionFailureScreen({
    required BuildContext context,
    required FeedbackEvent event,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Missão Não Concluída'),
        content:
            const Text('Não foi possível concluir a missão. Tente novamente.'),
        actions: [
          TextButton(
            onPressed: () =>
                _handleEventAction(context, event, FeedbackAction.retry),
            child: const Text('Tentar Novamente'),
          ),
          TextButton(
            onPressed: () =>
                _handleEventAction(context, event, FeedbackAction.goHome),
            child: const Text('Voltar ao Início'),
          ),
        ],
      ),
    );
  }

  /// Mostra tela de falha de trilha de aprendizado
  static Future<void> _showLearningPathFailureScreen({
    required BuildContext context,
    required FeedbackEvent event,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Trilha Não Concluída'),
        content: const Text(
            'Não foi possível concluir a trilha de aprendizado. Tente novamente.'),
        actions: [
          TextButton(
            onPressed: () =>
                _handleEventAction(context, event, FeedbackAction.retry),
            child: const Text('Tentar Novamente'),
          ),
          TextButton(
            onPressed: () =>
                _handleEventAction(context, event, FeedbackAction.goHome),
            child: const Text('Voltar ao Início'),
          ),
        ],
      ),
    );
  }

  /// Mostra tela customizada
  static Future<void> _showCustomScreen({
    required BuildContext context,
    required FeedbackEvent event,
  }) {
    return MinorAchievementScreen.show(
      context: context,
      rewardData: event.data,
      onContinue: () =>
          _handleEventAction(context, event, FeedbackAction.continueAction),
    );
  }
}
