import 'package:cryptoquest/presentation/widgets/crypto_card.dart';
import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("CryptoQuest"),
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.person),
          onPressed: () {
            // TODO Drawer do User
          },
        ),
        actions: [
          Image.asset(
            'assets/images/btc_purple.png',
            height: 40,
          )
        ],
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
