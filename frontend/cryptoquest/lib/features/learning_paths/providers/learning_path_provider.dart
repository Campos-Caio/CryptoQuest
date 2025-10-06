import 'package:flutter/foundation.dart';
import '../models/learning_path_model.dart';
import '../models/user_path_progress_model.dart';
import '../models/learning_path_response_model.dart';
import '../services/learning_path_service.dart';

class LearningPathProvider with ChangeNotifier {
  final LearningPathService _service = LearningPathService();

  // Estado das trilhas
  List<LearningPath> _learningPaths = [];
  Map<String, LearningPathResponse> _pathDetails = {};
  Map<String, UserPathProgress?> _userProgress = {};

  // Estado de loading
  bool _isLoading = false;
  bool _isLoadingDetails = false;
  bool _isStartingPath = false;
  bool _isCompletingMission = false;

  // Mensagens de erro
  String? _errorMessage;
  String? _detailsErrorMessage;

  // Flag para verificar se o provider foi disposed
  bool _disposed = false;

  // ==================== GETTERS ====================

  List<LearningPath> get learningPaths => _learningPaths;
  Map<String, LearningPathResponse> get pathDetails => _pathDetails;
  Map<String, UserPathProgress?> get userProgress => _userProgress;

  bool get isLoading => _isLoading;
  bool get isLoadingDetails => _isLoadingDetails;
  bool get isStartingPath => _isStartingPath;
  bool get isCompletingMission => _isCompletingMission;

  String? get errorMessage => _errorMessage;
  String? get detailsErrorMessage => _detailsErrorMessage;

  // ==================== MÉTODOS PÚBLICOS ====================

  /// Carrega todas as trilhas ativas
  Future<void> loadLearningPaths() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _learningPaths = await _service.getAllLearningPaths();
      _errorMessage = null;
    } catch (e) {
      _errorMessage = 'Erro ao carregar trilhas: $e';
      if (kDebugMode) {}
    } finally {
      _isLoading = false;
      if (!_disposed) {
        notifyListeners();
      }
    }
  }

  /// Carrega detalhes de uma trilha específica
  Future<LearningPathResponse?> loadPathDetails(
      String pathId, String? token) async {
    if (token == null) {
      _detailsErrorMessage = 'Token de autenticação não encontrado';
      return null;
    }

    _isLoadingDetails = true;
    _detailsErrorMessage = null;
    notifyListeners();

    try {
      if (kDebugMode) {}

      final details = await _service.getUserPathDetails(pathId, token);

      if (details != null) {
        _pathDetails[pathId] = details;
        _userProgress[pathId] = details.progress;

        if (kDebugMode) {}
      } else {
        _detailsErrorMessage = 'Trilha não encontrada';
      }

      return details;
    } catch (e) {
      _detailsErrorMessage = 'Erro ao carregar detalhes: $e';
      if (kDebugMode) {}
      return null;
    } finally {
      _isLoadingDetails = false;
      if (!_disposed) {
        notifyListeners();
      }
    }
  }

  /// Inicia uma trilha para o usuário
  Future<bool> startLearningPath(String pathId, String? token) async {
    if (token == null) {
      _errorMessage = 'Token de autenticação não encontrado';
      return false;
    }

    _isStartingPath = true;
    _errorMessage = null;
    notifyListeners();

    try {
      if (kDebugMode) {}

      final progress = await _service.startLearningPath(pathId, token);
      _userProgress[pathId] = progress;

      // Atualiza os detalhes se já estiverem carregados
      if (_pathDetails.containsKey(pathId)) {
        final currentDetails = _pathDetails[pathId]!;
        _pathDetails[pathId] = LearningPathResponse(
          path: currentDetails.path,
          progress: progress,
          stats: currentDetails.stats,
        );
      }

      if (kDebugMode) {}

      return true;
    } catch (e) {
      _errorMessage = 'Erro ao iniciar trilha: $e';
      if (kDebugMode) {}
      return false;
    } finally {
      _isStartingPath = false;
      if (!_disposed) {
        notifyListeners();
      }
    }
  }

  /// Conclui uma missão
  Future<bool> completeMission(
      String pathId, String missionId, List<int> answers, String? token,
      {List<double>? timePerQuestion,
      List<double>? confidenceLevels,
      List<int>? hintsUsed,
      List<int>? attemptsPerQuestion}) async {
    if (token == null) {
      _errorMessage = 'Token de autenticação não encontrado';
      return false;
    }

    _isCompletingMission = true;
    _errorMessage = null;
    notifyListeners();

    try {
      if (kDebugMode) {}

      final result = await _service.completeMission(
        pathId,
        missionId,
        answers,
        token,
        timePerQuestion: timePerQuestion,
        confidenceLevels: confidenceLevels,
        hintsUsed: hintsUsed,
        attemptsPerQuestion: attemptsPerQuestion,
      );

      // Atualiza o progresso
      if (result['progress'] != null) {
        final progress = UserPathProgress.fromJson(result['progress']);
        _userProgress[pathId] = progress;

        // Atualiza os detalhes se já estiverem carregados
        if (_pathDetails.containsKey(pathId)) {
          final currentDetails = _pathDetails[pathId]!;
          _pathDetails[pathId] = LearningPathResponse(
            path: currentDetails.path,
            progress: progress,
            stats: currentDetails.stats,
          );
        }
      }

      // Recarrega os detalhes da trilha para atualizar a interface
      await refreshPathDetails(pathId, token);

      if (kDebugMode) {}

      return true;
    } catch (e) {
      _errorMessage = 'Erro ao concluir missão: $e';
      if (kDebugMode) {}
      return false;
    } finally {
      _isCompletingMission = false;
      if (!_disposed) {
        notifyListeners();
      }
    }
  }

  /// Carrega o progresso do usuário em todas as trilhas
  Future<void> loadUserProgress(String? token) async {
    if (token == null) {
      _errorMessage = 'Token de autenticação não encontrado';
      return;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      if (kDebugMode) {}

      final progressList = await _service.getUserProgress(token);

      // Atualiza o mapa de progresso
      for (final progress in progressList) {
        _userProgress[progress.pathId] = progress;
      }

      if (kDebugMode) {}
    } catch (e) {
      _errorMessage = 'Erro ao carregar progresso: $e';
      if (kDebugMode) {}
    } finally {
      _isLoading = false;
      if (!_disposed) {
        notifyListeners();
      }
    }
  }

  // ==================== MÉTODOS AUXILIARES ====================

  /// Limpa mensagens de erro
  void clearErrors() {
    _errorMessage = null;
    _detailsErrorMessage = null;
    if (!_disposed) {
      notifyListeners();
    }
  }

  /// Verifica se o usuário já iniciou uma trilha
  bool hasUserStartedPath(String pathId) {
    return _userProgress.containsKey(pathId) && _userProgress[pathId] != null;
  }

  /// Verifica se o usuário completou uma trilha
  bool hasUserCompletedPath(String pathId) {
    final progress = _userProgress[pathId];
    return progress?.isCompleted ?? false;
  }

  /// Obtém o progresso de uma trilha específica
  UserPathProgress? getPathProgress(String pathId) {
    return _userProgress[pathId];
  }

  /// Obtém os detalhes de uma trilha específica
  LearningPathResponse? getPathDetails(String pathId) {
    return _pathDetails[pathId];
  }

  /// Recarrega os detalhes de uma trilha específica
  Future<void> refreshPathDetails(String pathId, String? token) async {
    if (token == null) return;

    try {
      final details = await _service.getUserPathDetails(pathId, token);
      if (details != null && !_disposed) {
        _pathDetails[pathId] = details;
        notifyListeners();
      }
    } catch (e) {
      if (kDebugMode) {}
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
