import 'package:cryptoquest/features/home/widgets/crypto_card.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/missions/widgets/mission_card.dart';
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
      Provider.of<MissionNotifier>(context, listen: false).fetchDailyMissions();
    });
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
          final authNotifier =
              Provider.of<AuthNotifier>(context, listen: false);
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
                    // Fecha o drawer e navega para a pagina de perfil
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
              return Center(
                child: CircularProgressIndicator(),
              );
            }

            if (missionNotifier.errorMessage != null) {
              return Center(
                child: Text(missionNotifier.errorMessage!),
              );
            }

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Missoes Diarias',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(
                  height: 16.0,
                ),
                Expanded(
                    child: ListView.builder(
                        itemCount: missionNotifier.dailyMissions.length,
                        itemBuilder: (context, index) {
                          final mission = missionNotifier.dailyMissions[index];
                          return MissionCard(mission: mission);
                        }))
              ],
            );
          },
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 25.0),
              child: Column(
                children: [
                  // Missão Diária
                  CryptoCard(
                    title: "Trilha Ativa",
                    subtitle: "BlockChain Basico",
                    icon: Icon(Icons.query_builder,
                        color: Color(0xFF00FFC8), size: 32),
                  ),

                  // Missão Diária
                  CryptoCard(
                    title: "Missao Diaria",
                    subtitle: "Complete um Quizz sobre BTC",
                    icon: Icon(Icons.check_circle,
                        color: Color(0xFF00FFC8), size: 32),
                  ),

                  // Ranking
                  CryptoCard(
                    title: "Ranking",
                    subtitle: "Ver Classificacao",
                    icon: Icon(Icons.emoji_events,
                        color: Color(0xFF00FFC8), size: 32),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
