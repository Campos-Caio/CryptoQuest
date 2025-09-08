import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/home/widgets/feature_card.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/missions/pages/missions_pages.dart';
import 'package:cryptoquest/features/learning_paths/learning_paths.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  void initState() {
    super.initState();
    // Pede ao MissionNotifier para buscar as missões assim que a tela é carregada
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
      final missionNotifier =
          Provider.of<MissionNotifier>(context, listen: false);
      final learningPathProvider =
          Provider.of<LearningPathProvider>(context, listen: false);

      if (authNotifier.token != null) {
        missionNotifier.fetchDailyMissions(authNotifier.token!);
        learningPathProvider.loadLearningPaths();
        learningPathProvider.loadUserProgress(authNotifier.token!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("CryptoQuest"),
        centerTitle: true,
        actions: [
          Image.asset(
            'assets/images/btc_purple.png',
            height: 40,
          )
        ],
      ),
      drawer: Consumer<AuthNotifier>(
        builder: (context, authNotifier, child) {
          return Drawer(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                UserAccountsDrawerHeader(
                  accountName:
                      Text(authNotifier.userProfile?.name ?? 'Usuario'),
                  accountEmail: Text(authNotifier.userProfile?.email ?? ""),
                  decoration: BoxDecoration(
                    color: Colors.deepPurple[700],
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.person),
                  title: const Text("Meu perfil"),
                  onTap: () {
                    Navigator.pop(context);
                    Navigator.pushNamed(context, '/profile');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.logout),
                  title: const Text("Sair"),
                  onTap: () {
                    authNotifier.logout();
                    Navigator.of(context)
                        .pushNamedAndRemoveUntil('/login', (route) => false);
                  },
                )
              ],
            ),
          );
        },
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            Consumer<LearningPathProvider>(
              builder: (context, learningPathProvider, child) {
                // Busca a primeira trilha ativa ou em progresso
                String title = "Trilhas de Aprendizado";
                String subtitle = "Explore novas trilhas";
                double progressValue = 0.0;
                String progressText = "0 / 0";

                if (learningPathProvider.learningPaths.isNotEmpty) {
                  final firstPath = learningPathProvider.learningPaths.first;
                  final pathProgress =
                      learningPathProvider.getPathProgress(firstPath.id);

                  if (pathProgress != null) {
                    title = firstPath.name;
                    subtitle = "Continue sua jornada";
                    progressValue = pathProgress.progressPercentage / 100;
                    progressText =
                        "${pathProgress.completedMissions.length} / ${firstPath.modules.fold(0, (sum, module) => sum + module.missions.length)}";
                  } else {
                    title = firstPath.name;
                    subtitle = "Inicie sua jornada";
                  }
                }

                return FeatureCard(
                  title: title,
                  subtitle: subtitle,
                  icon: Icons.rocket_launch_rounded,
                  iconColor: const Color(0xFF00FFC8),
                  trailing: learningPathProvider.learningPaths.isNotEmpty
                      ? SizedBox(
                          width: 120,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              LinearProgressIndicator(
                                value: progressValue,
                                color: const Color(0xFF00FFC8),
                                backgroundColor: Colors.white24,
                                minHeight: 6,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              const SizedBox(height: 6),
                              Align(
                                alignment: Alignment.centerRight,
                                child: Text(progressText,
                                    style: const TextStyle(
                                        color: Colors.white70, fontSize: 12)),
                              ),
                            ],
                          ),
                        )
                      : null,
                  onTap: () {
                    Navigator.pushNamed(context, '/learning-paths');
                  },
                );
              },
            ),
            FeatureCard(
              title: "Missão Diária",
              subtitle: "Complete um Quizz sobre BTC",
              icon: Icons.check_circle,
              iconColor: const Color(0xFF00FFC8),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const MissionsPages()),
                );
              },
            ),
            FeatureCard(
              title: "Ranking",
              subtitle: "Ver Classificação",
              icon: Icons.emoji_events,
              iconColor: const Color(0xFF00FFC8),
              onTap: () {
                // navegação futura para ranking
              },
            ),
          ],
        ),
      ),
    );
  }
}
