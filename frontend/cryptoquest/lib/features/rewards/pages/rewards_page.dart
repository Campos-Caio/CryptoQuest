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
    _tabController = TabController(length: 2, vsync: this);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadRewardsData();
    });
  }

  Future<void> _loadRewardsData() async {
    final rewardProvider = Provider.of<RewardProvider>(context, listen: false);
    await Future.wait([
      rewardProvider.loadUserBadges(),
      rewardProvider.loadAvailableBadges(),
    ]);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

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
            Tab(text: 'Minhas Badges', icon: Icon(Icons.emoji_events)),
            Tab(text: 'Disponíveis', icon: Icon(Icons.star)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildUserBadges(),
          _buildAvailableBadges(),
        ],
      ),
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
