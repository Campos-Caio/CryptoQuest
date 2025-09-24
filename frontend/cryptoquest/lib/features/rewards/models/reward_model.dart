class Reward {
  final String id;
  final String type;
  final String title;
  final String description;
  final int points;
  final int xp;
  final String? badgeId;
  final Map<String, dynamic> requirements;
  final bool isActive;
  final DateTime createdAt;

  Reward({
    required this.id,
    required this.type,
    required this.title,
    required this.description,
    required this.points,
    required this.xp,
    this.badgeId,
    required this.requirements,
    required this.isActive,
    required this.createdAt,
  });

  factory Reward.fromJson(Map<String, dynamic> json) {
    return Reward(
      id: json['id'],
      type: json['type'],
      title: json['title'],
      description: json['description'],
      points: json['points'],
      xp: json['xp'],
      badgeId: json['badge_id'],
      requirements: json['requirements'] ?? {},
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'description': description,
      'points': points,
      'xp': xp,
      'badge_id': badgeId,
      'requirements': requirements,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class UserReward {
  final String userId;
  final String? rewardId;
  final DateTime earnedAt;
  final int pointsEarned;
  final int xpEarned;
  final Map<String, dynamic> context;

  UserReward({
    required this.userId,
    this.rewardId,
    required this.earnedAt,
    required this.pointsEarned,
    required this.xpEarned,
    required this.context,
  });

  factory UserReward.fromJson(Map<String, dynamic> json) {
    return UserReward(
      userId: json['user_id'] ?? '',
      rewardId: json['reward_id'],
      earnedAt: DateTime.parse(json['earned_at']),
      pointsEarned: json['points_earned'] ?? 0,
      xpEarned: json['xp_earned'] ?? 0,
      context: json['context'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'reward_id': rewardId,
      'earned_at': earnedAt.toIso8601String(),
      'points_earned': pointsEarned,
      'xp_earned': xpEarned,
      'context': context,
    };
  }
}

class Badge {
  final String? id;
  final String? name;
  final String? description;
  final String? icon;
  final String? rarity;
  final String? color;

  Badge({
    this.id,
    this.name,
    this.description,
    this.icon,
    this.rarity,
    this.color,
  });

  factory Badge.fromJson(Map<String, dynamic> json) {
    return Badge(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      icon: json['icon'],
      rarity: json['rarity'],
      color: json['color'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'icon': icon,
      'rarity': rarity,
      'color': color,
    };
  }
}

class UserBadge {
  final String userId;
  final String? badgeId;
  final DateTime earnedAt;
  final Map<String, dynamic> context;

  UserBadge({
    required this.userId,
    this.badgeId,
    required this.earnedAt,
    required this.context,
  });

  factory UserBadge.fromJson(Map<String, dynamic> json) {
    return UserBadge(
      userId: json['user_id'] ?? '',
      badgeId: json['badge_id'],
      earnedAt: DateTime.parse(json['earned_at']),
      context: json['context'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'badge_id': badgeId,
      'earned_at': earnedAt.toIso8601String(),
      'context': context,
    };
  }
}
