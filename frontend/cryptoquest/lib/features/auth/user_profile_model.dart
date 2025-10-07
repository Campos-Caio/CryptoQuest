// Model para retornar o perfil do usuario.
class UserProfile {
  final String uid;
  final String name;
  final String email;
  final DateTime registerDate;
  final int level;
  final bool hasCompletedQuestionnaire;
  final int points;
  final int xp;
  final int currentStreak;
  final List<String> badges;

  UserProfile({
    required this.uid,
    required this.name,
    required this.email,
    required this.registerDate,
    required this.level,
    required this.hasCompletedQuestionnaire,
    this.points = 0,
    this.xp = 0,
    this.currentStreak = 0,
    this.badges = const [],
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      uid: json['uid'],
      name: json['name'],
      email: json['email'],
      registerDate: DateTime.parse(json['register_date']),
      level: json['level'] ?? 1,
      hasCompletedQuestionnaire: json['has_completed_questionnaire'] ?? false,
      points: json['points'] ?? 0,
      xp: json['xp'] ?? 0,
      currentStreak: json['current_streak'] ?? 0,
      badges: List<String>.from(json['badges'] ?? []),
    );
  }
}
