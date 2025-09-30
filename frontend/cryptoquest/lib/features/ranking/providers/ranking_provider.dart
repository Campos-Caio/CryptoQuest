import 'package:flutter/material.dart';
import 'package:cryptoquest/features/ranking/models/ranking_model.dart';
import 'package:cryptoquest/features/ranking/services/ranking_api_service.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';

class RankingProvider extends ChangeNotifier {
  final RankingApiService _apiService = RankingApiService();
  late final AuthNotifier authNotifier;

  RankingProvider({required this.authNotifier});

  bool _isLoading = false;
  String? _errorMessage;
  Ranking? _globalRanking;
  Ranking? _weeklyRanking;
  UserRankingStats? _userStats;

  // Getters
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  Ranking? get globalRanking => _globalRanking;
  Ranking? get weeklyRanking => _weeklyRanking;
  UserRankingStats? get userStats => _userStats;

  // Métodos públicos
  Future<void> loadGlobalRanking({int limit = 100}) async {
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
      _globalRanking = await _apiService.getGlobalRanking(token, limit: limit);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadWeeklyRanking() async {
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
      _weeklyRanking = await _apiService.getWeeklyRanking(token);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadUserRankingStats() async {
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

      _userStats = await _apiService.getUserRankingStats(userId, token);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refreshAllRankings() async {
    await Future.wait([
      loadGlobalRanking(),
      loadWeeklyRanking(),
      loadUserRankingStats(),
    ]);
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Métodos auxiliares
  RankingEntry? getUserRankingEntry() {
    if (_globalRanking == null || authNotifier.userProfile?.uid == null) {
      return null;
    }

    final userId = authNotifier.userProfile!.uid;
    try {
      return _globalRanking!.entries.firstWhere(
        (entry) => entry.userId == userId,
      );
    } catch (e) {
      return null;
    }
  }

  int getUserGlobalRank() {
    final userEntry = getUserRankingEntry();
    return userEntry?.rank ?? 0;
  }

  String getRankingPositionText() {
    final rank = getUserGlobalRank();
    if (rank == 0) return 'Não classificado';
    if (rank == 1) return '🥇 1º lugar';
    if (rank == 2) return '🥈 2º lugar';
    if (rank == 3) return '🥉 3º lugar';
    return '$rankº lugar';
  }

  String getPercentileText() {
    if (_userStats == null) return 'N/A';
    return 'Top ${(100 - _userStats!.percentile).toStringAsFixed(1)}%';
  }

  List<RankingEntry> getTopUsers({int limit = 10}) {
    if (_globalRanking == null) return [];
    return _globalRanking!.entries.take(limit).toList();
  }

  List<RankingEntry> getUsersAroundMe({int range = 5}) {
    if (_globalRanking == null || authNotifier.userProfile?.uid == null) {
      return [];
    }

    final userId = authNotifier.userProfile!.uid;
    final userIndex = _globalRanking!.entries.indexWhere(
      (entry) => entry.userId == userId,
    );

    if (userIndex == -1) return [];

    final start = (userIndex - range).clamp(0, _globalRanking!.entries.length);
    final end =
        (userIndex + range + 1).clamp(0, _globalRanking!.entries.length);

    return _globalRanking!.entries.sublist(start, end);
  }
}
