import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cryptoquest/features/ranking/providers/ranking_provider.dart';
import 'package:cryptoquest/features/ranking/models/ranking_model.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';

class RankingPage extends StatefulWidget {
  const RankingPage({super.key});

  @override
  State<RankingPage> createState() => _RankingPageState();
}

class _RankingPageState extends State<RankingPage>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final rankingProvider =
          Provider.of<RankingProvider>(context, listen: false);
      rankingProvider.refreshAllRankings();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ranking'),
        centerTitle: true,
        backgroundColor: const Color(0xFF6926C4),
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFF00FFC8),
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'Global', icon: Icon(Icons.public)),
            Tab(text: 'Semanal', icon: Icon(Icons.calendar_today)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildGlobalRanking(),
          _buildWeeklyRanking(),
        ],
      ),
    );
  }

  Widget _buildGlobalRanking() {
    return Consumer<RankingProvider>(
      builder: (context, rankingProvider, child) {
        if (rankingProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              color: Color(0xFF00FFC8),
            ),
          );
        }

        if (rankingProvider.errorMessage != null) {
          return _buildErrorWidget(rankingProvider.errorMessage!);
        }

        if (rankingProvider.globalRanking == null) {
          return const Center(
            child: Text(
              'Nenhum ranking disponível',
              style: TextStyle(color: Colors.white70),
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => rankingProvider.loadGlobalRanking(),
          color: const Color(0xFF00FFC8),
          child: Column(
            children: [
              _buildUserStatsCard(rankingProvider),
              Expanded(
                child: _buildRankingList(rankingProvider.globalRanking!),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildWeeklyRanking() {
    return Consumer<RankingProvider>(
      builder: (context, rankingProvider, child) {
        if (rankingProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              color: Color(0xFF00FFC8),
            ),
          );
        }

        if (rankingProvider.errorMessage != null) {
          return _buildErrorWidget(rankingProvider.errorMessage!);
        }

        if (rankingProvider.weeklyRanking == null) {
          return const Center(
            child: Text(
              'Nenhum ranking semanal disponível',
              style: TextStyle(color: Colors.white70),
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => rankingProvider.loadWeeklyRanking(),
          color: const Color(0xFF00FFC8),
          child: _buildRankingList(rankingProvider.weeklyRanking!),
        );
      },
    );
  }

  Widget _buildUserStatsCard(RankingProvider rankingProvider) {
    final userStats = rankingProvider.userStats;
    final userEntry = rankingProvider.getUserRankingEntry();

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF6926C4), Color(0xFF7F5AF0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Sua Posição',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    rankingProvider.getRankingPositionText(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              if (userEntry != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${userEntry.points} pts',
                      style: const TextStyle(
                        color: Color(0xFF00FFC8),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Nível ${userEntry.level}',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
            ],
          ),
          if (userStats != null) ...[
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(
                    'Percentil', rankingProvider.getPercentileText()),
                _buildStatItem('Total Usuários', '${userStats.totalUsers}'),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Color(0xFF00FFC8),
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildRankingList(Ranking ranking) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: ranking.entries.length,
      itemBuilder: (context, index) {
        final entry = ranking.entries[index];
        final isCurrentUser = entry.userId ==
            Provider.of<AuthNotifier>(context, listen: false).userProfile?.uid;

        return _buildRankingItem(entry, index + 1, isCurrentUser);
      },
    );
  }

  Widget _buildRankingItem(
      RankingEntry entry, int position, bool isCurrentUser) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isCurrentUser
            ? const Color(0xFF00FFC8).withOpacity(0.1)
            : const Color(0xFF242629),
        borderRadius: BorderRadius.circular(12),
        border: isCurrentUser
            ? Border.all(color: const Color(0xFF00FFC8), width: 2)
            : null,
      ),
      child: Row(
        children: [
          _buildRankIcon(position),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.name,
                  style: TextStyle(
                    color:
                        isCurrentUser ? const Color(0xFF00FFC8) : Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${entry.points} pontos • Nível ${entry.level}',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          if (entry.badges.isNotEmpty)
            Row(
              children: entry.badges.take(3).map((badge) {
                return Container(
                  margin: const EdgeInsets.only(left: 4),
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF00FFC8).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.emoji_events,
                    color: Color(0xFF00FFC8),
                    size: 16,
                  ),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildRankIcon(int position) {
    IconData icon;
    Color color;

    switch (position) {
      case 1:
        icon = Icons.emoji_events;
        color = const Color(0xFFFFD700); // Gold
        break;
      case 2:
        icon = Icons.emoji_events;
        color = const Color(0xFFC0C0C0); // Silver
        break;
      case 3:
        icon = Icons.emoji_events;
        color = const Color(0xFFCD7F32); // Bronze
        break;
      default:
        icon = Icons.person;
        color = const Color(0xFF00FFC8);
    }

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Icon(
        icon,
        color: color,
        size: 24,
      ),
    );
  }

  Widget _buildErrorWidget(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            color: Colors.red,
            size: 64,
          ),
          const SizedBox(height: 16),
          Text(
            'Erro ao carregar ranking',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              final rankingProvider =
                  Provider.of<RankingProvider>(context, listen: false);
              rankingProvider.refreshAllRankings();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFC8),
              foregroundColor: Colors.black,
            ),
            child: const Text('Tentar Novamente'),
          ),
        ],
      ),
    );
  }
}
