import 'package:flutter/material.dart' hide Badge;
import 'package:cryptoquest/features/rewards/models/reward_model.dart';
import 'package:cryptoquest/features/rewards/services/reward_api_service.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';

class RewardProvider extends ChangeNotifier {
  final RewardApiService _apiService = RewardApiService();
  late final AuthNotifier authNotifier;

  RewardProvider({required this.authNotifier});

  bool _isLoading = false;
  String? _errorMessage;
  List<UserReward> _userRewards = [];
  List<UserBadge> _userBadges = [];
  List<Badge> _availableBadges = [];

  // Getters
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<UserReward> get userRewards => _userRewards;
  List<UserBadge> get userBadges => _userBadges;
  List<Badge> get availableBadges => _availableBadges;

  // Métodos públicos
  Future<void> loadUserRewardsHistory() async {
    final token = authNotifier.token;
    if (token == null) {
      _errorMessage = 'Usuário não autenticado';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final userId = authNotifier.userProfile?.uid;
      if (userId == null) {
        throw Exception('ID do usuário não encontrado');
      }

      _userRewards = await _apiService.getUserRewardsHistory(userId, token);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadUserBadges() async {
    final token = authNotifier.token;
    if (token == null) {
      _errorMessage = 'Usuário não autenticado';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final userId = authNotifier.userProfile?.uid;
      if (userId == null) {
        throw Exception('ID do usuário não encontrado');
      }

      _userBadges = await _apiService.getUserBadges(userId, token);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadAvailableBadges() async {
    final token = authNotifier.token;
    if (token == null) {
      _errorMessage = 'Usuário não autenticado';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final userId = authNotifier.userProfile?.uid;
      if (userId == null) {
        throw Exception('ID do usuário não encontrado');
      }

      _availableBadges = await _apiService.getAvailableBadges(userId, token);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>?> awardMissionCompletion(
    String missionId,
    double score,
    String missionType,
  ) async {
    final token = authNotifier.token;
    if (token == null) {
      _errorMessage = 'Usuário não autenticado';
      notifyListeners();
      return null;
    }

    try {
      final userId = authNotifier.userProfile?.uid;
      if (userId == null) {
        throw Exception('ID do usuário não encontrado');
      }

      final result = await _apiService.awardMissionCompletion(
        userId,
        missionId,
        score,
        missionType,
        token,
      );

      // Recarregar dados após conceder recompensas
      await loadUserRewardsHistory();
      await loadUserBadges();

      return result;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Métodos auxiliares
  List<UserReward> getRecentRewards({int limit = 10}) {
    final sortedRewards = List<UserReward>.from(_userRewards);
    sortedRewards.sort((a, b) => b.earnedAt.compareTo(a.earnedAt));
    return sortedRewards.take(limit).toList();
  }

  int getTotalPointsEarned() {
    return _userRewards.fold(0, (sum, reward) => sum + reward.pointsEarned);
  }

  int getTotalXpEarned() {
    return _userRewards.fold(0, (sum, reward) => sum + reward.xpEarned);
  }

  List<UserBadge> getBadgesByRarity(String rarity) {
    return _userBadges.where((badge) {
      final badgeInfo = _availableBadges.firstWhere(
        (b) => b.id == badge.badgeId,
        orElse: () => Badge(
          id: '',
          name: '',
          description: '',
          icon: '',
          rarity: '',
          color: '',
        ),
      );
      return badgeInfo.rarity == rarity;
    }).toList();
  }

  // Método para buscar informações completas de um badge conquistado
  Badge getBadgeInfoForUserBadge(UserBadge userBadge) {
    // Primeiro, tentar encontrar na lista de badges disponíveis
    final availableBadge = _availableBadges.firstWhere(
      (b) => b.id == userBadge.badgeId,
      orElse: () => Badge(),
    );

    // Se encontrou, retornar
    if (availableBadge.id != null && availableBadge.id!.isNotEmpty) {
      return availableBadge;
    }

    // Se não encontrou, buscar na lista de todos os badges (incluindo conquistados)
    // Vamos fazer uma busca mais ampla
    return _getBadgeInfoFromAllBadges(userBadge.badgeId);
  }

  // Método auxiliar para buscar badge em todos os badges do sistema
  Badge _getBadgeInfoFromAllBadges(String? badgeId) {
    if (badgeId == null || badgeId.isEmpty) {
      return Badge(
        id: '',
        name: 'Badge Desconhecido',
        description: 'Informações não disponíveis',
        icon: '🏆',
        rarity: 'common',
        color: '#00FFC8',
      );
    }

    // Por enquanto, retornar um badge genérico baseado no ID
    // Em uma implementação mais robusta, faríamos uma chamada à API
    return Badge(
      id: badgeId,
      name: _getBadgeNameById(badgeId),
      description: _getBadgeDescriptionById(badgeId),
      icon: _getBadgeIconById(badgeId),
      rarity: 'common',
      color: '#00FFC8',
    );
  }

  // Métodos auxiliares para mapear IDs de badges para informações
  String _getBadgeNameById(String badgeId) {
    switch (badgeId) {
      case 'perfectionist':
        return 'Perfeccionista';
      case 'first_steps':
        return 'Primeiros Passos';
      case 'streak_7':
        return 'Streak de 7 Dias';
      case 'streak_30':
        return 'Streak de 30 Dias';
      case 'level_up':
        return 'Subiu de Nível';
      default:
        return 'Badge Especial';
    }
  }

  String _getBadgeDescriptionById(String badgeId) {
    switch (badgeId) {
      case 'perfectionist':
        return 'Acertou 100% em uma missão';
      case 'first_steps':
        return 'Completou sua primeira missão';
      case 'streak_7':
        return 'Manteve atividade por 7 dias';
      case 'streak_30':
        return 'Manteve atividade por 30 dias';
      case 'level_up':
        return 'Subiu de nível';
      default:
        return 'Badge conquistado com sucesso';
    }
  }

  String _getBadgeIconById(String badgeId) {
    switch (badgeId) {
      case 'perfectionist':
        return '🎯';
      case 'first_steps':
        return '👶';
      case 'streak_7':
        return '🔥';
      case 'streak_30':
        return '💪';
      case 'level_up':
        return '⬆️';
      default:
        return '🏆';
    }
  }
}
