class RankingEntry {
  final String userId;
  final String name;
  final String email;
  final int points;
  final int xp;
  final int level;
  final int rank;
  final String? avatarUrl;
  final List<String> badges;
  final DateTime lastActivity;

  RankingEntry({
    required this.userId,
    required this.name,
    required this.email,
    required this.points,
    required this.xp,
    required this.level,
    required this.rank,
    this.avatarUrl,
    required this.badges,
    required this.lastActivity,
  });

  factory RankingEntry.fromJson(Map<String, dynamic> json) {
    return RankingEntry(
      userId: json['user_id'] ?? '',
      name: json['name'] ?? 'Usuário',
      email: json['email'] ?? '',
      points: json['points'] ?? 0,
      xp: json['xp'] ?? 0,
      level: json['level'] ?? 1,
      rank: json['rank'] ?? 0,
      avatarUrl: json['avatar_url'],
      badges: List<String>.from(json['badges'] ?? []),
      lastActivity:
          DateTime.tryParse(json['last_activity'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'name': name,
      'email': email,
      'points': points,
      'xp': xp,
      'level': level,
      'rank': rank,
      'avatar_url': avatarUrl,
      'badges': badges,
      'last_activity': lastActivity.toIso8601String(),
    };
  }
}

class Ranking {
  final String type;
  final String period;
  final List<RankingEntry> entries;
  final int totalUsers;
  final DateTime generatedAt;

  Ranking({
    required this.type,
    required this.period,
    required this.entries,
    required this.totalUsers,
    required this.generatedAt,
  });

  factory Ranking.fromJson(Map<String, dynamic> json) {
    return Ranking(
      type: json['type'],
      period: json['period'],
      entries: (json['entries'] as List)
          .map((e) => RankingEntry.fromJson(e))
          .toList(),
      totalUsers: json['total_users'],
      generatedAt: DateTime.parse(json['generated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'period': period,
      'entries': entries.map((e) => e.toJson()).toList(),
      'total_users': totalUsers,
      'generated_at': generatedAt.toIso8601String(),
    };
  }
}

class UserRankingStats {
  final String userId;
  final int globalRank;
  final int weeklyRank;
  final int monthlyRank;
  final int levelRank;
  final int totalUsers;
  final double percentile;
  final DateTime lastUpdated;

  UserRankingStats({
    required this.userId,
    required this.globalRank,
    required this.weeklyRank,
    required this.monthlyRank,
    required this.levelRank,
    required this.totalUsers,
    required this.percentile,
    required this.lastUpdated,
  });

  factory UserRankingStats.fromJson(Map<String, dynamic> json) {
    return UserRankingStats(
      userId: json['user_id'] ?? '',
      globalRank: json['global_rank'] ?? 0,
      weeklyRank: json['weekly_rank'] ?? 0,
      monthlyRank: json['monthly_rank'] ?? 0,
      levelRank: json['level_rank'] ?? 0,
      totalUsers: json['total_users'] ?? 0,
      percentile: (json['percentile'] ?? 0.0).toDouble(),
      lastUpdated:
          DateTime.tryParse(json['last_updated'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'global_rank': globalRank,
      'weekly_rank': weeklyRank,
      'monthly_rank': monthlyRank,
      'level_rank': levelRank,
      'total_users': totalUsers,
      'percentile': percentile,
      'last_updated': lastUpdated.toIso8601String(),
    };
  }
}
