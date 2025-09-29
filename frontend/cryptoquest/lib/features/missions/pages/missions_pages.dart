import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/missions/widgets/mission_card.dart';
import 'package:cryptoquest/features/quiz/pages/quiz_page.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class MissionsPages extends StatefulWidget {
  const MissionsPages({super.key});

  @override
  State<MissionsPages> createState() => _MissionsPagesState();
}

class _MissionsPagesState extends State<MissionsPages> {
  @override
  void initState() {
    super.initState();
    // Carrega as missoes ao entrar na pagina
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthNotifier>(context, listen: false);
      final missions = Provider.of<MissionNotifier>(context, listen: false);

      if (auth.token != null) {
        missions.fetchDailyMissions(auth.token!);
      }
    });
  }

  void _onMissionTap(Mission mission) {
    if (mission.type == 'QUIZ') {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => QuizPage(
              missionId: mission.id,
              quizId: mission.contentId,
              missionTitle: mission.title),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text('Missão ${mission.type} ainda não implementada')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final missionNotifier = Provider.of<MissionNotifier>(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Missões Diárias'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: missionNotifier.isLoading
            ? const Center(child: CircularProgressIndicator())
            : missionNotifier.errorMessage != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(missionNotifier.errorMessage!),
                        const SizedBox(
                          height: 12,
                        ),
                        ElevatedButton(
                          onPressed: () {
                            final auth = Provider.of<AuthNotifier>(context,
                                listen: false);
                            if (auth.token != null) {
                              missionNotifier.fetchDailyMissions(auth.token!);
                            }
                          },
                          child: const Text("Tentar novamente"),
                        )
                      ],
                    ),
                  )
                : missionNotifier.dailyMissions.isEmpty
                    ? const Center(
                        child: Text("Nenhuma missão disponível hoje"),
                      )
                    : ListView.builder(
                        itemCount: missionNotifier.dailyMissions.length,
                        itemBuilder: (context, index) {
                          final mission = missionNotifier.dailyMissions[index];
                          return MissionCard(
                              mission: mission,
                              onTap: () => _onMissionTap(mission));
                        },
                      ),
      ),
    );
  }
}
