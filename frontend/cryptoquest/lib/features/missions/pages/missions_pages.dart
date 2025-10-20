import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/missions/widgets/mission_card.dart';
import 'package:cryptoquest/features/quiz/pages/quiz_page.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/shared/widgets/widgets.dart';
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
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: missionNotifier.isLoading
            ? const SkeletonLoading(itemCount: 7, itemHeight: 100)
            : missionNotifier.errorMessage != null
                ? ErrorStateWidget(
                    message: missionNotifier.errorMessage!,
                    onRetry: () {
                      final auth =
                          Provider.of<AuthNotifier>(context, listen: false);
                      if (auth.token != null) {
                        missionNotifier.fetchDailyMissions(auth.token!);
                      }
                    },
                  )
                : missionNotifier.dailyMissions.isEmpty
                    ? const EmptyStateWidget(
                        title: 'Nenhuma missão disponível',
                        subtitle: 'Volte amanhã para novas missões diárias!',
                        icon: Icons.assignment_outlined,
                        iconColor: AppColors.accent,
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
