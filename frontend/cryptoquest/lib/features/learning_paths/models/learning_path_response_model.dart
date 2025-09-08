import 'learning_path_model.dart';
import 'user_path_progress_model.dart';

class LearningPathResponse {
  final LearningPath path;
  final UserPathProgress? progress;
  final Map<String, dynamic> stats;

  LearningPathResponse({
    required this.path,
    this.progress,
    required this.stats,
  });

  factory LearningPathResponse.fromJson(Map<String, dynamic> json) {
    return LearningPathResponse(
      path: LearningPath.fromJson(json['path'] ?? {}),
      progress: json['progress'] != null
          ? UserPathProgress.fromJson(json['progress'])
          : null,
      stats: Map<String, dynamic>.from(json['stats'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'path': path.toJson(),
      'progress': progress?.toJson(),
      'stats': stats,
    };
  }

  // Getters para facilitar o acesso às estatísticas
  int get totalModules => stats['total_modules'] ?? 0;
  int get totalMissions => stats['total_missions'] ?? 0;
  int get completedModules => stats['completed_modules'] ?? 0;
  int get completedMissions => stats['completed_missions'] ?? 0;
  double get progressPercentage =>
      (stats['progress_percentage'] ?? 0.0).toDouble();
  bool get isStarted => stats['is_started'] ?? false;
  bool get isCompleted => stats['is_completed'] ?? false;
}
