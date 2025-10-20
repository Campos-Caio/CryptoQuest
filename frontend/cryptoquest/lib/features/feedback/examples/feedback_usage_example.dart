/// Exemplos de uso do sistema de feedback
///
/// Este arquivo contém exemplos práticos de como usar
/// o sistema de feedback em diferentes contextos

import 'package:flutter/material.dart';
import 'package:cryptoquest/features/feedback/feedback.dart';

/// Exemplo 1: Feedback após completar quiz
void showQuizFeedbackExample(BuildContext context) {
  // Dados simulados do resultado
  final missionResult = {
    'xp': 250,
    'points': 100,
    'level': 3,
    'previous_level': 2,
  };

  FeedbackService.showMissionCompleteFeedback(
    context: context,
    missionResult: missionResult,
    previousXP: 400,
    currentXP: 650,
    previousLevel: 2,
    currentLevel: 3,
    streakDays: 5,
    quizPercentage: 85.0,
    badges: [
      BadgeData(
        id: 'first_win',
        name: 'Primeira Vitória',
        description: 'Complete sua primeira missão',
        icon: '🏆',
        rarity: 'common',
      ),
    ],
    onContinue: () {
      // Navegar para próxima tela
    },
  );
}

/// Exemplo 2: Feedback rápido para ações menores
void showQuickFeedbackExample(BuildContext context) {
  FeedbackService.showQuickFeedback(
    context: context,
    message: 'Missão diária completada!',
    xpGained: 50,
    pointsGained: 25,
    icon: Icons.check_circle,
    color: Colors.green,
  );
}

/// Exemplo 3: Notificação de badge
void showBadgeNotificationExample(BuildContext context) {
  final badge = BadgeData(
    id: 'streak_7',
    name: 'Sequência de 7 Dias',
    description: 'Mantenha uma sequência de 7 dias consecutivos',
    icon: '🔥',
    rarity: 'rare',
  );

  FeedbackService.showBadgeNotification(
    context: context,
    badge: badge,
    onTap: () {
      Navigator.pushNamed(context, '/rewards');
    },
  );
}

/// Exemplo 4: Feedback customizado usando RewardSummarySheet diretamente
void showCustomFeedbackExample(BuildContext context) {
  final rewardData = RewardFeedbackModel(
    xpGained: 500,
    pointsGained: 250,
    previousXP: 1000,
    currentXP: 1500,
    previousLevel: 3,
    currentLevel: 4,
    leveledUp: true,
    badgesEarned: [
      BadgeData(
        id: 'master',
        name: 'Mestre Bitcoin',
        description: 'Complete todas as missões de Bitcoin',
        icon: '👑',
        rarity: 'legendary',
      ),
    ],
    streakDays: 10,
    quizPercentage: 95.0,
    isSuccess: true,
    message: 'Você é um verdadeiro mestre!',
  );

  RewardSummarySheet.show(
    context: context,
    rewardData: rewardData,
    onContinue: () {
      // Ação personalizada
    },
    onViewProfile: () {
      Navigator.pushNamed(context, '/profile');
    },
    onViewBadges: () {
      Navigator.pushNamed(context, '/rewards');
    },
  );
}
