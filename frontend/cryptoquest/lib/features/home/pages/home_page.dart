import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/home/widgets/feature_card.dart';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/quiz/pages/quiz_page.dart';
import 'package:cryptoquest/features/missions/pages/missions_pages.dart';
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

      if (authNotifier.token != null) {
        missionNotifier.fetchDailyMissions(authNotifier.token!);
      }
    });
  }

  void _onMissionTap(BuildContext context, Mission mission) {
    if (mission.type == 'QUIZ') {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => QuizPage(
            missionId: mission.id,
            quizId: mission.contentId,
            missionTitle: mission.title,
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Funcionalidade ${mission.type} em desenvolvimento'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authNotifier = Provider.of<AuthNotifier>(context);

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
            FeatureCard(
              title: "Trilha Ativa",
              subtitle: "BlockChain Básico",
              icon: Icons.rocket_launch_rounded,
              iconColor: const Color(0xFF00FFC8),
              trailing: SizedBox(
                width: 120,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    LinearProgressIndicator(
                      value: 3 / 5,
                      color: const Color(0xFF00FFC8),
                      backgroundColor: Colors.white24,
                      minHeight: 6,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    const SizedBox(height: 6),
                    const Align(
                      alignment: Alignment.centerRight,
                      child: Text("3 / 5",
                          style:
                              TextStyle(color: Colors.white70, fontSize: 12)),
                    ),
                  ],
                ),
              ),
              onTap: () {
                // navegação futura para a trilha ativa
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
