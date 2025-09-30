import 'package:flutter/material.dart' hide Badge;
import 'package:provider/provider.dart';
import 'package:cryptoquest/features/rewards/providers/reward_provider.dart';
import 'package:cryptoquest/features/rewards/models/reward_model.dart';

class RewardsPage extends StatefulWidget {
  const RewardsPage({super.key});

  @override
  State<RewardsPage> createState() => _RewardsPageState();
}

class _RewardsPageState extends State<RewardsPage>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadRewardsData();
    });
  }

  // 🎯 NOVO MÉTODO: Carregar dados de recompensas
  Future<void> _loadRewardsData() async {
    final rewardProvider = Provider.of<RewardProvider>(context, listen: false);
    await Future.wait([
      rewardProvider.loadUserRewardsHistory(),
      rewardProvider.loadUserBadges(),
      rewardProvider.loadAvailableBadges(),
    ]);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // 🎯 NOVO MÉTODO: Atualizar quando a tela for focada
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Atualizar dados quando a tela for focada (ex: voltando de uma missão)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadRewardsData();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Recompensas'),
        centerTitle: true,
        backgroundColor: const Color(0xFF6926C4),
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFF00FFC8),
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'Histórico', icon: Icon(Icons.history)),
            Tab(text: 'Badges', icon: Icon(Icons.emoji_events)),
            Tab(text: 'Disponíveis', icon: Icon(Icons.star)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildRewardsHistory(),
          _buildUserBadges(),
          _buildAvailableBadges(),
        ],
      ),
    );
  }

  Widget _buildRewardsHistory() {
    return Consumer<RewardProvider>(
      builder: (context, rewardProvider, child) {
        if (rewardProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              color: Color(0xFF00FFC8),
            ),
          );
        }

        if (rewardProvider.errorMessage != null) {
          return _buildErrorWidget(rewardProvider.errorMessage!);
        }

        if (rewardProvider.userRewards.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.card_giftcard,
                  color: Colors.white70,
                  size: 64,
                ),
                SizedBox(height: 16),
                Text(
                  'Nenhuma recompensa ainda',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 18,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Complete missões para ganhar recompensas!',
                  style: TextStyle(
                    color: Colors.white54,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => rewardProvider.loadUserRewardsHistory(),
          color: const Color(0xFF00FFC8),
          child: Column(
            children: [
              _buildStatsCard(rewardProvider),
              Expanded(
                child: _buildRewardsList(rewardProvider.userRewards),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildUserBadges() {
    return Consumer<RewardProvider>(
      builder: (context, rewardProvider, child) {
        if (rewardProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              color: Color(0xFF00FFC8),
            ),
          );
        }

        if (rewardProvider.errorMessage != null) {
          return _buildErrorWidget(rewardProvider.errorMessage!);
        }

        if (rewardProvider.userBadges.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.emoji_events,
                  color: Colors.white70,
                  size: 64,
                ),
                SizedBox(height: 16),
                Text(
                  'Nenhum badge conquistado',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 18,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Complete desafios para ganhar badges!',
                  style: TextStyle(
                    color: Colors.white54,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => rewardProvider.loadUserBadges(),
          color: const Color(0xFF00FFC8),
          child: _buildBadgesGrid(
              rewardProvider.userBadges, rewardProvider.availableBadges),
        );
      },
    );
  }

  Widget _buildAvailableBadges() {
    return Consumer<RewardProvider>(
      builder: (context, rewardProvider, child) {
        if (rewardProvider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              color: Color(0xFF00FFC8),
            ),
          );
        }

        if (rewardProvider.errorMessage != null) {
          return _buildErrorWidget(rewardProvider.errorMessage!);
        }

        if (rewardProvider.availableBadges.isEmpty) {
          return const Center(
            child: Text(
              'Nenhum badge disponível',
              style: TextStyle(color: Colors.white70),
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => rewardProvider.loadAvailableBadges(),
          color: const Color(0xFF00FFC8),
          child: _buildBadgesGrid([], rewardProvider.availableBadges),
        );
      },
    );
  }

  Widget _buildStatsCard(RewardProvider rewardProvider) {
    final totalPoints = rewardProvider.getTotalPointsEarned();
    final totalXp = rewardProvider.getTotalXpEarned();
    final recentRewards = rewardProvider.getRecentRewards(limit: 5);

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
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('Total Pontos', '$totalPoints', Icons.stars),
              _buildStatItem('Total XP', '$totalXp', Icons.trending_up),
              _buildStatItem('Recompensas',
                  '${rewardProvider.userRewards.length}', Icons.card_giftcard),
            ],
          ),
          if (recentRewards.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Divider(color: Colors.white30),
            const SizedBox(height: 8),
            Text(
              'Recompensas Recentes',
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            ...recentRewards
                .take(3)
                .map((reward) => _buildRecentRewardItem(reward)),
          ],
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: const Color(0xFF00FFC8),
          size: 24,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Color(0xFF00FFC8),
            fontSize: 18,
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

  Widget _buildRecentRewardItem(UserReward reward) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '${reward.pointsEarned} pts',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
            ),
          ),
          Text(
            '${reward.earnedAt.day}/${reward.earnedAt.month}',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRewardsList(List<UserReward> rewards) {
    final sortedRewards = List<UserReward>.from(rewards);
    sortedRewards.sort((a, b) => b.earnedAt.compareTo(a.earnedAt));

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: sortedRewards.length,
      itemBuilder: (context, index) {
        final reward = sortedRewards[index];
        return _buildRewardItem(reward);
      },
    );
  }

  Widget _buildRewardItem(UserReward reward) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF242629),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF00FFC8).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: const Color(0xFF00FFC8).withOpacity(0.2),
              borderRadius: BorderRadius.circular(24),
            ),
            child: const Icon(
              Icons.card_giftcard,
              color: Color(0xFF00FFC8),
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Recompensa Conquistada',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${reward.pointsEarned} pontos • ${reward.xpEarned} XP',
                  style: const TextStyle(
                    color: Color(0xFF00FFC8),
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatDate(reward.earnedAt),
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBadgesGrid(
      List<UserBadge> userBadges, List<Badge> availableBadges) {
    final badgesToShow = userBadges.isEmpty ? availableBadges : userBadges;
    final isUserBadges = userBadges.isNotEmpty;

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.8,
      ),
      itemCount: badgesToShow.length,
      itemBuilder: (context, index) {
        if (isUserBadges) {
          final userBadge = userBadges[index];
          final rewardProvider =
              Provider.of<RewardProvider>(context, listen: false);
          final badge = rewardProvider.getBadgeInfoForUserBadge(userBadge);
          return _buildBadgeItem(badge, userBadge.earnedAt, true);
        } else {
          final badge = availableBadges[index];
          final hasBadge = userBadges.any((ub) => ub.badgeId == badge.id);
          return _buildBadgeItem(badge, null, hasBadge);
        }
      },
    );
  }

  Widget _buildBadgeItem(Badge badge, DateTime? earnedAt, bool isEarned) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isEarned
            ? const Color(0xFF00FFC8).withOpacity(0.1)
            : const Color(0xFF242629),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isEarned
              ? const Color(0xFF00FFC8)
              : const Color(0xFF00FFC8).withOpacity(0.3),
          width: isEarned ? 2 : 1,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: isEarned
                  ? const Color(0xFF00FFC8).withOpacity(0.2)
                  : Colors.grey.withOpacity(0.2),
              borderRadius: BorderRadius.circular(32),
            ),
            child: Center(
              child: Text(
                badge.icon ?? '',
                style: const TextStyle(fontSize: 32),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            badge.name ?? '',
            style: TextStyle(
              color: isEarned ? const Color(0xFF00FFC8) : Colors.white70,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            badge.description ?? '',
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          if (earnedAt != null) ...[
            const SizedBox(height: 8),
            Text(
              'Conquistado em ${_formatDate(earnedAt)}',
              style: const TextStyle(
                color: Color(0xFF00FFC8),
                fontSize: 10,
              ),
            ),
          ],
        ],
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
          const Text(
            'Erro ao carregar recompensas',
            style: TextStyle(
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
              final rewardProvider =
                  Provider.of<RewardProvider>(context, listen: false);
              rewardProvider.loadUserRewardsHistory();
              rewardProvider.loadUserBadges();
              rewardProvider.loadAvailableBadges();
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

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
  }
}
