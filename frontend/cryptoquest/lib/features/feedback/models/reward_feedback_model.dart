/// Modelo para dados de feedback de recompensas
///
/// Contém todas as informações necessárias para exibir
/// feedback visual ao usuário após completar uma ação
class RewardFeedbackModel {
  final int xpGained;
  final int pointsGained;
  final int previousXP;
  final int currentXP;
  final int previousLevel;
  final int currentLevel;
  final bool leveledUp;
  final List<BadgeData> badgesEarned;
  final int streakDays;
  final double quizPercentage;
  final bool isSuccess;
  final String? message;

  RewardFeedbackModel({
    required this.xpGained,
    required this.pointsGained,
    required this.previousXP,
    required this.currentXP,
    required this.previousLevel,
    required this.currentLevel,
    this.leveledUp = false,
    this.badgesEarned = const [],
    this.streakDays = 0,
    this.quizPercentage = 0.0,
    this.isSuccess = true,
    this.message,
  });

  /// Cria instância a partir de dados da API
  factory RewardFeedbackModel.fromApiResponse(Map<String, dynamic> json) {
    return RewardFeedbackModel(
      xpGained: json['xp_gained'] ?? 0,
      pointsGained: json['points_gained'] ?? 0,
      previousXP: json['previous_xp'] ?? 0,
      currentXP: json['current_xp'] ?? 0,
      previousLevel: json['previous_level'] ?? 1,
      currentLevel: json['current_level'] ?? 1,
      leveledUp: json['leveled_up'] ?? false,
      badgesEarned: (json['badges_earned'] as List<dynamic>?)
              ?.map((badge) => BadgeData.fromJson(badge))
              .toList() ??
          [],
      streakDays: json['streak_days'] ?? 0,
      quizPercentage: (json['quiz_percentage'] ?? 0.0).toDouble(),
      isSuccess: json['is_success'] ?? true,
      message: json['message'],
    );
  }

  /// Verifica se há recompensas significativas para mostrar
  bool get hasSignificantRewards {
    return xpGained > 0 ||
        pointsGained > 0 ||
        badgesEarned.isNotEmpty ||
        leveledUp;
  }

  /// Determina o tipo de celebração baseado nas recompensas
  CelebrationType get celebrationType {
    if (leveledUp) return CelebrationType.levelUp;
    if (badgesEarned.any((badge) => badge.rarity == 'legendary')) {
      return CelebrationType.legendary;
    }
    if (badgesEarned.length >= 3) return CelebrationType.multiple;
    if (badgesEarned.isNotEmpty) return CelebrationType.badge;
    if (xpGained >= 500) return CelebrationType.major;
    if (xpGained > 0) return CelebrationType.minor;
    return CelebrationType.none;
  }
}

/// Dados de um badge conquistado
class BadgeData {
  final String id;
  final String name;
  final String description;
  final String icon;
  final String rarity;
  final String? color;

  BadgeData({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    this.rarity = 'common',
    this.color,
  });

  factory BadgeData.fromJson(Map<String, dynamic> json) {
    return BadgeData(
      id: json['id'] ?? '',
      name: json['name'] ?? 'Badge',
      description: json['description'] ?? '',
      icon: json['icon'] ?? '🏆',
      rarity: json['rarity'] ?? 'common',
      color: json['color'],
    );
  }

  /// Retorna cor baseada na raridade
  String get rarityColor {
    switch (rarity.toLowerCase()) {
      case 'legendary':
        return '#FFD700'; // Dourado
      case 'epic':
        return '#9C27B0'; // Roxo
      case 'rare':
        return '#2196F3'; // Azul
      case 'uncommon':
        return '#4CAF50'; // Verde
      default:
        return '#9E9E9E'; // Cinza
    }
  }
}

/// Tipos de celebração baseados na magnitude da conquista
enum CelebrationType {
  none, // Sem celebração
  minor, // Pequena (snackbar)
  badge, // Badge único (bottom sheet)
  multiple, // Múltiplos badges (bottom sheet expandido)
  major, // Conquista grande (bottom sheet com confetti)
  levelUp, // Level up (fullscreen)
  legendary, // Badge lendário (fullscreen com animação especial)
}
