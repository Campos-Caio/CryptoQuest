import 'package:flutter/foundation.dart';
import '../services/ai_service.dart';

class AIProvider extends ChangeNotifier {
  // Estado do perfil de IA
  Map<String, dynamic>? _aiProfile;
  List<Map<String, dynamic>> _recommendations = [];
  Map<String, dynamic>? _insights;
  Map<String, dynamic>? _modelMetrics;

  // Estados de loading
  bool _isLoadingProfile = false;
  bool _isLoadingRecommendations = false;
  bool _isLoadingInsights = false;
  bool _isLoadingMetrics = false;

  // Estados de erro
  String? _profileError;
  String? _recommendationsError;
  String? _insightsError;
  String? _metricsError;

  // Getters
  Map<String, dynamic>? get aiProfile => _aiProfile;
  List<Map<String, dynamic>> get recommendations => _recommendations;
  Map<String, dynamic>? get insights => _insights;
  Map<String, dynamic>? get modelMetrics => _modelMetrics;

  bool get isLoadingProfile => _isLoadingProfile;
  bool get isLoadingRecommendations => _isLoadingRecommendations;
  bool get isLoadingInsights => _isLoadingInsights;
  bool get isLoadingMetrics => _isLoadingMetrics;

  String? get profileError => _profileError;
  String? get recommendationsError => _recommendationsError;
  String? get insightsError => _insightsError;
  String? get metricsError => _metricsError;

  bool get hasData =>
      _aiProfile != null || _recommendations.isNotEmpty || _insights != null;
  bool get hasErrors =>
      _profileError != null ||
      _recommendationsError != null ||
      _insightsError != null;

  /// Carrega o perfil de IA do usuário
  Future<void> loadAIProfile(String userId, String token) async {
    _isLoadingProfile = true;
    _profileError = null;
    notifyListeners();

    try {
      final profile = await AIService.getUserAIProfile(userId, token);
      if (profile != null) {
        _aiProfile = profile;
      } else {
        _profileError = 'Não foi possível carregar o perfil de IA';
      }
    } catch (e) {
      _profileError = 'Erro ao carregar perfil: $e';
    } finally {
      _isLoadingProfile = false;
      notifyListeners();
    }
  }

  /// Carrega as recomendações do usuário
  Future<void> loadRecommendations(String userId, String token,
      {int limit = 5}) async {
    _isLoadingRecommendations = true;
    _recommendationsError = null;
    notifyListeners();

    try {
      final recommendations =
          await AIService.getUserRecommendations(userId, token, limit: limit);
      _recommendations = recommendations;
    } catch (e) {
      _recommendationsError = 'Erro ao carregar recomendações: $e';
    } finally {
      _isLoadingRecommendations = false;
      notifyListeners();
    }
  }

  /// Carrega os insights do usuário
  Future<void> loadInsights(String userId, String token) async {
    _isLoadingInsights = true;
    _insightsError = null;
    notifyListeners();

    try {
      final insights = await AIService.getUserInsights(userId, token);
      if (insights != null) {
        _insights = insights;
      } else {
        _insightsError = 'Não foi possível carregar os insights';
      }
    } catch (e) {
      _insightsError = 'Erro ao carregar insights: $e';
    } finally {
      _isLoadingInsights = false;
      notifyListeners();
    }
  }

  /// Carrega métricas dos modelos (para administradores)
  Future<void> loadModelMetrics(String token) async {
    _isLoadingMetrics = true;
    _metricsError = null;
    notifyListeners();

    try {
      final metrics = await AIService.getAIModelMetrics(token);
      if (metrics != null) {
        _modelMetrics = metrics;
      } else {
        _metricsError = 'Não foi possível carregar as métricas';
      }
    } catch (e) {
      _metricsError = 'Erro ao carregar métricas: $e';
    } finally {
      _isLoadingMetrics = false;
      notifyListeners();
    }
  }

  /// Carrega todos os dados de IA do usuário
  Future<void> loadAllAIData(String userId, String token) async {
    await Future.wait([
      loadAIProfile(userId, token),
      loadRecommendations(userId, token),
      loadInsights(userId, token),
    ]);
  }

  /// Busca sugestão de dificuldade para um domínio
  Future<Map<String, dynamic>?> getDifficultySuggestion(
      String userId, String domain, String token) async {
    try {
      return await AIService.getDifficultySuggestion(userId, domain, token);
    } catch (e) {
      print('Erro ao buscar sugestão de dificuldade: $e');
      return null;
    }
  }

  /// Busca sugestões de conteúdo para um domínio
  Future<List<Map<String, dynamic>>> getContentSuggestions(
      String userId, String domain, String token,
      {int limit = 3}) async {
    try {
      return await AIService.getContentSuggestions(userId, domain, token,
          limit: limit);
    } catch (e) {
      print('Erro ao buscar sugestões de conteúdo: $e');
      return [];
    }
  }

  /// Verifica se a IA está habilitada
  Future<bool> isAIEnabled(String token) async {
    try {
      return await AIService.isAIEnabled(token);
    } catch (e) {
      print('Erro ao verificar status da IA: $e');
      return false;
    }
  }

  /// Limpa todos os dados carregados
  void clearData() {
    _aiProfile = null;
    _recommendations.clear();
    _insights = null;
    _modelMetrics = null;

    _profileError = null;
    _recommendationsError = null;
    _insightsError = null;
    _metricsError = null;

    notifyListeners();
  }

  /// Recarrega todos os dados
  Future<void> refresh(String userId, String token) async {
    clearData();
    await loadAllAIData(userId, token);
  }

  /// Métodos utilitários para acessar dados específicos
  String? get learningStyle => _aiProfile?['learning_pattern']?['type'];
  double? get bitcoinProficiency =>
      _aiProfile?['performance_summary']?['bitcoin_proficiency'];
  double? get ethereumProficiency =>
      _aiProfile?['performance_summary']?['ethereum_proficiency'];
  double? get defiProficiency =>
      _aiProfile?['performance_summary']?['defi_proficiency'];
  double? get engagementScore =>
      _aiProfile?['performance_summary']?['engagement_score'];
  double? get consistencyScore =>
      _aiProfile?['performance_summary']?['consistency_score'];
  int? get dataPoints => _aiProfile?['data_points'];
  bool? get aiEnabled => _aiProfile?['ai_enabled'];

  /// Métodos para insights
  String? get idealTime => _insights?['ideal_time'];
  double? get avgResponseTime => _insights?['avg_response_time'];
  String? get focusArea => _insights?['focus_area'];
}
