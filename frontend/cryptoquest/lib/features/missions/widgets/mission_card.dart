import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:flutter/material.dart';

class MissionCard extends StatelessWidget {
  final Mission mission;
  final VoidCallback? onTap;
  const MissionCard({super.key, required this.mission, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16.0),
      child: ListTile(
        leading: Icon(
            mission.type == 'QUIZ' 
              ? Icons.quiz 
              : Icons.article,
          color: Colors.green,
        ),
        title: Text(
          mission.title,
          style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(mission.description),
        trailing: Text("+${mission.rewardPoints}XP"),
        onTap: onTap ?? () {
          print("Iniciando missao: ${mission.id}");
        },
      ),
    );
  }
}
