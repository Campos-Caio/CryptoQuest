import 'package:cryptoquest/features/home/widgets/crypto_card.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

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
        builder: (context, authNotifier, child){
          final authNotifier = Provider.of<AuthNotifier>(context, listen: false);

          return Drawer(
          child: ListView(
            padding: EdgeInsets.zero,
            children: [
              UserAccountsDrawerHeader(
                accountName: Text(authNotifier.userProfile?.name ?? 'Usuario'),
                accountEmail: Text(authNotifier.userProfile?.email ?? ""),
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
      body: Center(
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
    );
  }
}
