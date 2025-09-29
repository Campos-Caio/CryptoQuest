class UserPathProgress {
  final String userId;
  final String pathId;
  final DateTime startedAt;
  final DateTime? completedAt;
  final String? currentModuleId;
  final List<String> completedModules;
  final List<String> completedMissions;
  final int totalScore;
  final double progressPercentage;

  UserPathProgress({
    required this.userId,
    required this.pathId,
    required this.startedAt,
    this.completedAt,
    this.currentModuleId,
    required this.completedModules,
    required this.completedMissions,
    required this.totalScore,
    required this.progressPercentage,
  });

  factory UserPathProgress.fromJson(Map<String, dynamic> json) {
    return UserPathProgress(
      userId: json['user_id'] ?? '',
      pathId: json['path_id'] ?? '',
      startedAt: _parseDateTime(json['started_at']),
      completedAt: json['completed_at'] != null
          ? _parseDateTime(json['completed_at'])
          : null,
      currentModuleId: json['current_module_id'],
      completedModules: List<String>.from(json['completed_modules'] ?? []),
      completedMissions: List<String>.from(json['completed_missions'] ?? []),
      totalScore: json['total_score'] ?? 0,
      progressPercentage: (json['progress_percentage'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'path_id': pathId,
      'started_at': startedAt.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'current_module_id': currentModuleId,
      'completed_modules': completedModules,
      'completed_missions': completedMissions,
      'total_score': totalScore,
      'progress_percentage': progressPercentage,
    };
  }

  static DateTime _parseDateTime(dynamic dateTime) {
    if (dateTime is String) {
      return DateTime.parse(dateTime);
    } else if (dateTime is Map<String, dynamic> &&
        dateTime.containsKey('_seconds')) {
      // Firestore Timestamp
      return DateTime.fromMillisecondsSinceEpoch(dateTime['_seconds'] * 1000);
    } else {
      return DateTime.now();
    }
  }

  bool get isCompleted => completedAt != null;
  bool get isStarted => startedAt != DateTime.fromMillisecondsSinceEpoch(0);
}
