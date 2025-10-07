class LearningPath {
  final String id;
  final String name;
  final String description;
  final String difficulty;
  final String estimatedDuration;
  final List<String> prerequisites;
  final List<Module> modules;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  LearningPath({
    required this.id,
    required this.name,
    required this.description,
    required this.difficulty,
    required this.estimatedDuration,
    required this.prerequisites,
    required this.modules,
    required this.isActive,
    required this.createdAt,
    this.updatedAt,
  });

  factory LearningPath.fromJson(Map<String, dynamic> json) {
    return LearningPath(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      difficulty: json['difficulty'] ?? 'beginner',
      estimatedDuration: json['estimated_duration'] ?? '',
      prerequisites: List<String>.from(json['prerequisites'] ?? []),
      modules: (json['modules'] as List<dynamic>?)
              ?.map((module) => Module.fromJson(module))
              .toList() ??
          [],
      isActive: json['is_active'] ?? true,
      createdAt: _parseDateTime(json['created_at']),
      updatedAt: json['updated_at'] != null
          ? _parseDateTime(json['updated_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'difficulty': difficulty,
      'estimated_duration': estimatedDuration,
      'prerequisites': prerequisites,
      'modules': modules.map((module) => module.toJson()).toList(),
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
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
}

class Module {
  final String id;
  final String name;
  final String description;
  final int order;
  final List<MissionReference> missions;

  Module({
    required this.id,
    required this.name,
    required this.description,
    required this.order,
    required this.missions,
  });

  factory Module.fromJson(Map<String, dynamic> json) {
    return Module(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      order: json['order'] ?? 0,
      missions: (json['missions'] as List<dynamic>?)
              ?.map((mission) => MissionReference.fromJson(mission))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'order': order,
      'missions': missions.map((mission) => mission.toJson()).toList(),
    };
  }
}

class MissionReference {
  final String id;
  final String missionId; // ID real do quiz/missão
  final int order;
  final int requiredScore;

  MissionReference({
    required this.id,
    required this.missionId,
    required this.order,
    required this.requiredScore,
  });

  factory MissionReference.fromJson(Map<String, dynamic> json) {
    return MissionReference(
      id: json['id'] ?? '',
      missionId: json['mission_id'] ?? json['id'] ?? '', // Prioriza mission_id
      order: json['order'] ?? 0,
      requiredScore: json['required_score'] ?? 70,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'mission_id': missionId,
      'order': order,
      'required_score': requiredScore,
    };
  }
}
