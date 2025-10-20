/// Modelo para dados de conquistas e progresso
///
/// Usado para exibir informações detalhadas sobre
/// o progresso do usuário após completar ações
class AchievementData {
  final String title;
  final String subtitle;
  final AchievementType type;
  final int value;
  final String? icon;
  final bool isNew;

  AchievementData({
    required this.title,
    required this.subtitle,
    required this.type,
    required this.value,
    this.icon,
    this.isNew = false,
  });

  /// Cria achievement de XP ganho
  factory AchievementData.xp({
    required int amount,
    required int total,
  }) {
    return AchievementData(
      title: '+$amount XP',
      subtitle: 'Total: $total XP',
      type: AchievementType.xp,
      value: amount,
      icon: '⭐',
      isNew: true,
    );
  }

  /// Cria achievement de pontos ganhos
  factory AchievementData.points({
    required int amount,
    required int total,
  }) {
    return AchievementData(
      title: '+$amount Pontos',
      subtitle: 'Total: $total pontos',
      type: AchievementType.points,
      value: amount,
      icon: '💰',
      isNew: true,
    );
  }

  /// Cria achievement de streak
  factory AchievementData.streak({
    required int days,
  }) {
    return AchievementData(
      title: 'Sequência de $days dias',
      subtitle: 'Continue assim!',
      type: AchievementType.streak,
      value: days,
      icon: '🔥',
      isNew: false,
    );
  }

  /// Cria achievement de level up
  factory AchievementData.levelUp({
    required int newLevel,
  }) {
    return AchievementData(
      title: 'Nível $newLevel Alcançado!',
      subtitle: 'Você evoluiu!',
      type: AchievementType.levelUp,
      value: newLevel,
      icon: '🎖️',
      isNew: true,
    );
  }
}

/// Tipos de conquistas
enum AchievementType {
  xp,
  points,
  badge,
  streak,
  levelUp,
  mission,
  path,
}
