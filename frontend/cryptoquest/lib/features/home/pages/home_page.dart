import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/home/widgets/feature_card.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/missions/pages/missions_pages.dart';
import 'package:cryptoquest/features/learning_paths/learning_paths.dart';
import 'package:cryptoquest/features/learning_paths/widgets/ai_recommendation_home_card.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  // Widget para exibir estatísticas no drawer (otimizado)
  Widget _StatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(8), // Reduzido de 12 para 8
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(10), // Reduzido de 12 para 10
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min, // Adicionado para otimizar espaço
        children: [
          Icon(
            icon,
            color: color,
            size: 20, // Reduzido de 24 para 20
          ),
          const SizedBox(height: 4), // Reduzido de 8 para 4
          Text(
            value,
            style: TextStyle(
              fontSize: 16, // Reduzido de 18 para 16
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 10, // Reduzido de 12 para 10
              color: color.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

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
        // 🚀 OTIMIZAÇÃO: Carregar recomendações PRIMEIRO (prioridade)
        learningPathProvider.loadRecommendedLearningPaths(authNotifier.token!,
            limit: 2);

        // Carregar outros dados em paralelo
        missionNotifier.fetchDailyMissions(authNotifier.token!);
        learningPathProvider.loadLearningPaths();
        learningPathProvider.loadUserProgress(authNotifier.token!);
      }
    });
  }

  // Método helper para otimizar loading das recomendações
  Widget _buildRecommendationsLoading() {
    return Container(
      height: 80,
      margin: const EdgeInsets.only(bottom: 16),
      child: Center(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                color: AppColors.accent,
                strokeWidth: 2,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Carregando recomendações...',
              style: TextStyle(
                color: AppColors.onSurfaceVariant,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Método helper para seção de recomendações
  Widget _buildRecommendationsSection(
      LearningPathProvider learningPathProvider) {
    if (learningPathProvider.isLoadingRecommendations) {
      return _buildRecommendationsLoading();
    }

    if (learningPathProvider.recommendationsErrorMessage != null) {
      return const SizedBox.shrink();
    }

    if (learningPathProvider.aiRecommendations.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              Icon(
                Icons.psychology,
                color: AppColors.accent,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Recomendado para você',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.onSurface,
                ),
              ),
              const Spacer(),
              TextButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/learning-paths');
                },
                child: Text(
                  'Ver todas',
                  style: TextStyle(
                    color: AppColors.accent,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        ),
        AIRecommendationHomeCard(
          recommendation: learningPathProvider.aiRecommendations.first,
          onTap: () {
            final pathId = learningPathProvider
                .aiRecommendations.first['path_id'] as String?;
            if (pathId != null) {
              Navigator.pushNamed(
                context,
                '/learning-path-details',
                arguments: pathId,
              );
            }
          },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("CryptoQuest"),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
        elevation: 0,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Image.asset(
              'assets/images/btc_purple.png',
              height: 40,
            ),
          )
        ],
      ),
      drawer: Consumer2<AuthNotifier, LearningPathProvider>(
        builder: (context, authNotifier, learningPathProvider, child) {
          final userProfile = authNotifier.userProfile;
          final level = userProfile?.level ?? 1;
          final points = userProfile?.points ?? 0;
          final xp = userProfile?.xp ?? 0;
          final streak = userProfile?.currentStreak ?? 0;
          final badges = userProfile?.badges ?? [];

          // Calcular XP necessário para próximo nível (fórmula simples)
          final xpForNextLevel = level * 1000;
          final xpProgress = xp % 1000;
          final progressPercentage = xpProgress / 1000;

          return Drawer(
            child: SingleChildScrollView(
              // Adicionado para garantir scroll se necessário
              child: Column(
                children: [
                  // Header melhorado com informações do usuário
                  Container(
                    height: 160,
                    decoration: const BoxDecoration(
                      gradient: AppColors.primaryGradient,
                    ),
                    child: SafeArea(
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Avatar e informações básicas
                            Row(
                              children: [
                                CircleAvatar(
                                  radius: 25,
                                  backgroundColor:
                                      Colors.white.withOpacity(0.2),
                                  child: Text(
                                    (userProfile?.name.isNotEmpty == true
                                        ? userProfile!.name[0].toUpperCase()
                                        : 'U'),
                                    style: const TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        userProfile?.name ?? 'Usuário',
                                        style: const TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.white,
                                        ),
                                      ),
                                      Text(
                                        userProfile?.email ?? '',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.white.withOpacity(0.8),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),

                            // Nível e XP
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Text(
                                    'Nível $level',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Text(
                                    '$points pts',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                                if (streak > 0) ...[
                                  const SizedBox(width: 12),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 12, vertical: 6),
                                    decoration: BoxDecoration(
                                      color: Colors.orange.withOpacity(0.8),
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        const Icon(
                                          Icons.local_fire_department,
                                          color: Colors.white,
                                          size: 16,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          '$streak dias',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 14,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ],
                            ),
                            const SizedBox(height: 12),

                            // Barra de progresso do XP
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      'XP: $xpProgress/$xpForNextLevel',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 12,
                                      ),
                                    ),
                                    Text(
                                      '${(progressPercentage * 100).toInt()}%',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                LinearProgressIndicator(
                                  value: progressPercentage,
                                  backgroundColor:
                                      Colors.white.withOpacity(0.3),
                                  valueColor:
                                      const AlwaysStoppedAnimation<Color>(
                                    Colors.white,
                                  ),
                                  minHeight: 4,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  // Seção de Estatísticas Rápidas
                  Container(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Estatísticas',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: _StatCard(
                                icon: Icons.emoji_events,
                                label: 'Badges',
                                value: badges.length.toString(),
                                color: Colors.amber,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _StatCard(
                                icon: Icons.school,
                                label: 'Trilhas',
                                value: learningPathProvider.learningPaths.length
                                    .toString(),
                                color: AppColors.primary,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const Divider(height: 1),

                  // Navegação Principal
                  ListTile(
                    leading: const Icon(Icons.home),
                    title: const Text("Início"),
                    onTap: () {
                      Navigator.pop(context);
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.assignment),
                    title: const Text("Missões"),
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(context, '/missions');
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.school),
                    title: const Text("Trilhas de Aprendizado"),
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(context, '/learning-paths');
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.leaderboard),
                    title: const Text("Ranking"),
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(context, '/ranking');
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.card_giftcard),
                    title: const Text("Recompensas"),
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(context, '/rewards');
                    },
                  ),

                  const Divider(height: 1),

                  // Seção de Perfil e Configurações
                  ListTile(
                    leading: const Icon(Icons.person),
                    title: const Text("Meu Perfil"),
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(context, '/profile');
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.psychology),
                    title: const Text("Perfil de IA"),
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(context, '/ai-profile');
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.settings),
                    title: const Text("Configurações"),
                    onTap: () {
                      Navigator.pop(context);
                      // TODO: Implementar tela de configurações
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Configurações em desenvolvimento'),
                        ),
                      );
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.help),
                    title: const Text("Ajuda"),
                    onTap: () {
                      Navigator.pop(context);
                      // TODO: Implementar tela de ajuda
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Ajuda em desenvolvimento'),
                        ),
                      );
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.info),
                    title: const Text("Sobre"),
                    onTap: () {
                      Navigator.pop(context);
                      showAboutDialog(
                        context: context,
                        applicationName: 'CryptoQuest',
                        applicationVersion: '1.0.0',
                        applicationIcon: const Icon(Icons.currency_bitcoin),
                        children: [
                          const Text(
                            'Uma plataforma educacional gamificada para aprender sobre criptomoedas e blockchain.',
                          ),
                        ],
                      );
                    },
                  ),

                  const Divider(height: 1),

                  // Logout
                  ListTile(
                    leading: const Icon(Icons.logout, color: Colors.red),
                    title:
                        const Text("Sair", style: TextStyle(color: Colors.red)),
                    onTap: () {
                      Navigator.pop(context);
                      showDialog(
                        context: context,
                        builder: (context) => AlertDialog(
                          title: const Text('Confirmar Logout'),
                          content: const Text('Tem certeza que deseja sair?'),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: const Text('Cancelar'),
                            ),
                            TextButton(
                              onPressed: () {
                                Navigator.pop(context);
                                authNotifier.logout();
                                Navigator.of(context).pushNamedAndRemoveUntil(
                                  '/login',
                                  (route) => false,
                                );
                              },
                              child: const Text('Sair'),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          );
        },
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            // 🎯 PRIORIDADE 1: Recomendações de IA (primeiro item)
            Consumer<LearningPathProvider>(
              builder: (context, learningPathProvider, child) {
                return _buildRecommendationsSection(learningPathProvider);
              },
            ),

            // 🎯 PRIORIDADE 2: Trilha principal do usuário
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
                  iconColor: AppColors.accent,
                  trailing: learningPathProvider.learningPaths.isNotEmpty
                      ? SizedBox(
                          width: 120,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              LinearProgressIndicator(
                                value: progressValue,
                                color: AppColors.accent,
                                backgroundColor: AppColors.surfaceVariant,
                                minHeight: 6,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              const SizedBox(height: 6),
                              Align(
                                alignment: Alignment.centerRight,
                                child: Text(progressText,
                                    style: TextStyle(
                                        color: AppColors.onSurfaceVariant,
                                        fontSize: 12)),
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
              iconColor: AppColors.accent,
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
                Navigator.pushNamed(context, '/ranking');
              },
            ),
            FeatureCard(
              title: "Recompensas",
              subtitle: "Ver Badges e Conquistas",
              icon: Icons.card_giftcard,
              iconColor: const Color(0xFF00FFC8),
              onTap: () {
                Navigator.pushNamed(context, '/rewards');
              },
            ),
          ],
        ),
      ),
    );
  }
}
