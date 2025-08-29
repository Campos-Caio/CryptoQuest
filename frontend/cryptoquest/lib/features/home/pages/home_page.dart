import 'package:cryptoquest/features/home/widgets/crypto_card.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/missions/widgets/mission_card.dart';
import 'package:cryptoquest/features/quiz/pages/quiz_page.dart';
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
      final missionNotifier = Provider.of<MissionNotifier>(context, listen: false);
      
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
                  accountName: Text(authNotifier.userProfile?.name ?? 'Usuario'),
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
        child: Consumer<MissionNotifier>(
          builder: (context, missionNotifier, child) {
            if (missionNotifier.isLoading) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            if (missionNotifier.errorMessage != null) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(missionNotifier.errorMessage!),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
                        if (authNotifier.token != null) {
                          missionNotifier.fetchDailyMissions(authNotifier.token!);
                        }
                      },
                      child: const Text('Tentar Novamente'),
                    ),
                  ],
                ),
              );
            }

            if (missionNotifier.dailyMissions.isEmpty) {
              return const Center(
                child: Text('Nenhuma missão disponível hoje'),
              );
            }

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Missões Diárias',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 16.0),
                Expanded(
                  child: ListView.builder(
                    itemCount: missionNotifier.dailyMissions.length,
                    itemBuilder: (context, index) {
                      final mission = missionNotifier.dailyMissions[index];
                      return MissionCard(
                        mission: mission,
                        onTap: () => _onMissionTap(context, mission),
                      );
                    },
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}