import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/missions/services/mission_api_service.dart';
import 'package:flutter/material.dart';

class MissionNotifier extends ChangeNotifier {
  final MissionApiService _apiService = MissionApiService();
  final AuthNotifier authNotifier;

  MissionNotifier({required this.authNotifier});

  bool _isLoading = false;
  List<Mission> _dailyMissions = [];
  String? _errorMessage;

  bool get isLoading => _isLoading;
  List<Mission> get dailyMissions => _dailyMissions;
  String? get errorMessage => _errorMessage;

  //Busca as msisoes diarias do backend e atualiza o estado
  Future<void> fetchDailyMissions() async {
    final token = authNotifier.token;
    if (token == null) {
      _errorMessage = 'Usuário não autenticado.';
      notifyListeners();
      return;
    }

    _isLoading = true;
    notifyListeners();

    try {
      _dailyMissions = await _apiService.getDailyMissions(token);
      _errorMessage = null;
    } catch (error) {
      _errorMessage = error.toString();
    } finally {
      _isLoading = false;
      notifyListeners(); 
    }
  }
}
