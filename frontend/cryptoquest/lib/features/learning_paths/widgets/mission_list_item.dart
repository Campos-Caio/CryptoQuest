import 'package:flutter/material.dart';
import '../models/learning_path_model.dart';
import '../models/user_path_progress_model.dart';

class MissionListItem extends StatelessWidget {
  final MissionReference mission;
  final UserPathProgress? progress;
  final VoidCallback? onTap;
  final bool isLocked;

  const MissionListItem({
    Key? key,
    required this.mission,
    this.progress,
    this.onTap,
    this.isLocked = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isCompleted =
        progress?.completedMissions.contains(mission.id) ?? false;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      child: InkWell(
        onTap: isLocked ? null : onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            color: isLocked
                ? Colors.grey[100]
                : isCompleted
                    ? Colors.green[50]
                    : Colors.white,
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                // Ícone da missão
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: _getMissionColor(isCompleted, isLocked),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    _getMissionIcon(isCompleted, isLocked),
                    color: Colors.white,
                    size: 20,
                  ),
                ),

                const SizedBox(width: 12),

                // Conteúdo da missão
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Título da missão
                      Text(
                        'Missão ${mission.order}',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: isLocked ? Colors.grey[400] : Colors.black87,
                        ),
                      ),

                      const SizedBox(height: 2),

                      // Descrição da missão
                      Text(
                        'Quiz de conhecimento',
                        style: TextStyle(
                          fontSize: 12,
                          color: isLocked ? Colors.grey[400] : Colors.grey[600],
                        ),
                      ),

                      const SizedBox(height: 4),

                      // Pontuação necessária
                      Row(
                        children: [
                          Icon(
                            Icons.star,
                            size: 12,
                            color: isLocked
                                ? Colors.grey[400]
                                : Colors.orange[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'Mínimo: ${mission.requiredScore}%',
                            style: TextStyle(
                              fontSize: 11,
                              color: isLocked
                                  ? Colors.grey[400]
                                  : Colors.orange[600],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Indicador de status
                if (isCompleted)
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.green,
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Icon(
                      Icons.check,
                      color: Colors.white,
                      size: 16,
                    ),
                  )
                else if (isLocked)
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.grey,
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Icon(
                      Icons.lock,
                      color: Colors.white,
                      size: 16,
                    ),
                  )
                else
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Icon(
                      Icons.play_arrow,
                      color: Colors.white,
                      size: 16,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getMissionColor(bool isCompleted, bool isLocked) {
    if (isLocked) return Colors.grey;
    if (isCompleted) return Colors.green;
    return Colors.blue;
  }

  IconData _getMissionIcon(bool isCompleted, bool isLocked) {
    if (isLocked) return Icons.lock;
    if (isCompleted) return Icons.check_circle;
    return Icons.quiz;
  }
}
