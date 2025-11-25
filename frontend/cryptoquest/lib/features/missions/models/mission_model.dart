class Mission {
  final String id;
  final String title;
  final String description;
  final String type;
  final int rewardPoints;
  final int rewardXp;
  final int requiredLevel;
  final String contentId;

  Mission({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.rewardPoints,
    required this.rewardXp,
    required this.requiredLevel,
    required this.contentId,
  });

  factory Mission.fromJson(Map<String, dynamic> json) {
    return Mission(
      id: json['_id'] ?? json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      type: json['type'] ?? '',
      rewardPoints: json['reward_points'] ?? 0,
      rewardXp: json['reward_xp'] ?? 0,
      requiredLevel: json['required_level'] ?? 1,
      contentId: json['content_id'] ?? '',
    );
  }
}
