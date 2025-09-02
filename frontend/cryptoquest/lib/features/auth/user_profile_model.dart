// Model para retornar o perfil do usuario.
class UserProfile {
  final String uid;
  final String name;
  final String email;
  final DateTime registerDate;
  final int level;
  final bool hasCompletedQuestionnaire;

  UserProfile({
    required this.uid,
    required this.name,
    required this.email,
    required this.registerDate,
    required this.level,
    required this.hasCompletedQuestionnaire,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      uid: json['uid'],
      name: json['name'],
      email: json['email'],
      registerDate: DateTime.parse(json['register_date']),
      level: json['level'],
      hasCompletedQuestionnaire: json['has_completed_questionnaire'] ?? false,
    );
  }
}
