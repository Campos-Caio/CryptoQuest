import 'package:flutter/material.dart';
import '../services/mission_api_service.dart';
import '../models/mission_model.dart';
import '../../quiz/models/quiz_model.dart';

class MissionNotifier extends ChangeNotifier {
  final MissionApiService _apiService = MissionApiService();

  // Estado
  List<Mission> _dailyMissions = [];
  bool _isLoading = false;
  String? _errorMessage;

  // Estado do quiz
  Quiz? _currentQuiz;
  bool _isLoadingQuiz = false;
  String? _quizError;

  // Estado de submissão
  bool _isSubmitting = false;
  String? _submitError;
  Map<String, dynamic>? _lastCompletedMission;

  // Getters
  List<Mission> get dailyMissions => _dailyMissions;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  Quiz? get currentQuiz => _currentQuiz;
  bool get isLoadingQuiz => _isLoadingQuiz;
  String? get quizError => _quizError;
  bool get isSubmitting => _isSubmitting;
  String? get submitError => _submitError;
  Map<String, dynamic>? get lastCompletedMission => _lastCompletedMission;

  // Carregar missões elegíveis (filtradas por nível e status de conclusão)
  Future<void> fetchDailyMissions(String token) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final missions = await _apiService.getDailyMissions(token);

      _dailyMissions = missions;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  // Carregar quiz específico
  Future<Quiz?> loadQuiz(String quizId, String token) async {
    try {
      _isLoadingQuiz = true;
      _quizError = null;
      WidgetsBinding.instance.addPostFrameCallback((_) => notifyListeners());

      final quiz = await _apiService.getQuiz(quizId, token);

      _currentQuiz = quiz;
      _isLoadingQuiz = false;
      WidgetsBinding.instance.addPostFrameCallback((_) => notifyListeners());

      return quiz;
    } catch (e) {
      _quizError = e.toString();
      _isLoadingQuiz = false;
      WidgetsBinding.instance.addPostFrameCallback((_) => notifyListeners());
      return null;
    }
  }

  // Completar missão
  Future<Map<String, dynamic>?> completeMission(
      String missionId, List<int> answers, String token) async {
    try {
      _isSubmitting = true;
      _submitError = null;
      notifyListeners();

      final result =
          await _apiService.completeMission(missionId, answers, token);

      // Remover a missão completada da lista
      _dailyMissions.removeWhere((mission) => mission.id == missionId);
      _isSubmitting = false;
      _lastCompletedMission = result;
      notifyListeners();

      // Retornar o resultado para que possa ser usado para atualizar o AuthNotifier
      return result;
    } catch (e) {
      _submitError = e.toString();
      _isSubmitting = false;
      notifyListeners();
      // Re-throw o erro para que seja capturado pelo quiz_page.dart
      rethrow;
    }
  }

  // Limpar erros
  void clearErrors() {
    _errorMessage = null;
    _quizError = null;
    _submitError = null;
    notifyListeners();
  }

  // Limpar quiz atual
  void clearCurrentQuiz() {
    _currentQuiz = null;
    _quizError = null;
    notifyListeners();
  }

  // Definir dados da última missão completada
  void setLastCompletedMission(Map<String, dynamic> result) {
    _lastCompletedMission = result;
    notifyListeners();
  }
}
