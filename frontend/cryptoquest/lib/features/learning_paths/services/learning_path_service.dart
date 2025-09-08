import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/learning_path_model.dart';
import '../models/user_path_progress_model.dart';
import '../models/learning_path_response_model.dart';

class LearningPathService {
  static const String baseUrl = 'http://localhost:8000';

  // Headers padrão
  Map<String, String> _getHeaders(String? token) {
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // ==================== ENDPOINTS PÚBLICOS ====================

  /// Busca todas as trilhas ativas
  Future<List<LearningPath>> getAllLearningPaths() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/learning-paths/'),
        headers: _getHeaders(null),
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(response.body);
        return jsonList.map((json) => LearningPath.fromJson(json)).toList();
      } else {
        throw Exception('Erro ao buscar trilhas: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro na requisição: $e');
    }
  }

  /// Busca uma trilha específica por ID
  Future<LearningPath?> getLearningPathById(String pathId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/learning-paths/$pathId'),
        headers: _getHeaders(null),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return LearningPath.fromJson(json);
      } else if (response.statusCode == 404) {
        return null;
      } else {
        throw Exception('Erro ao buscar trilha: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro na requisição: $e');
    }
  }

  // ==================== ENDPOINTS AUTENTICADOS ====================

  /// Busca detalhes completos de uma trilha com progresso do usuário
  Future<LearningPathResponse?> getUserPathDetails(
      String pathId, String token) async {
    try {
      print('🔍 [Service] Buscando detalhes da trilha: $pathId');
      final response = await http.get(
        Uri.parse('$baseUrl/learning-paths/$pathId/details'),
        headers: _getHeaders(token),
      );

      print('📡 [Service] Status da resposta: ${response.statusCode}');
      print('📡 [Service] Corpo da resposta: ${response.body}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        print('✅ [Service] JSON decodificado com sucesso');
        return LearningPathResponse.fromJson(json);
      } else if (response.statusCode == 404) {
        print('❌ [Service] Trilha não encontrada');
        return null;
      } else {
        print('❌ [Service] Erro HTTP: ${response.statusCode}');
        print('❌ [Service] Resposta: ${response.body}');
        throw Exception(
            'Erro ao buscar detalhes: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('❌ [Service] Erro na requisição: $e');
      throw Exception('Erro na requisição: $e');
    }
  }

  /// Inicia uma trilha para o usuário
  Future<UserPathProgress> startLearningPath(
      String pathId, String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/learning-paths/$pathId/start'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return UserPathProgress.fromJson(json);
      } else {
        final errorBody = jsonDecode(response.body);
        throw Exception(
            'Erro ao iniciar trilha: ${errorBody['detail'] ?? response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro na requisição: $e');
    }
  }

  /// Conclui uma missão e atualiza o progresso
  Future<Map<String, dynamic>> completeMission(
      String pathId, String missionId, List<int> answers, String token) async {
    try {
      print('🔍 [Service] Completando missão: $missionId da trilha: $pathId');

      final response = await http.post(
        Uri.parse(
            '$baseUrl/learning-paths/$pathId/missions/$missionId/complete'),
        headers: _getHeaders(token),
        body: json.encode({
          'answers': answers,
        }),
      );

      print('📊 [Service] Status da resposta: ${response.statusCode}');
      print('📄 [Service] Corpo da resposta: ${response.body}');

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorBody = jsonDecode(response.body);
        final errorMessage = errorBody['detail'] ?? 'Erro desconhecido';
        throw Exception('$errorMessage (${response.statusCode})');
      }
    } catch (e) {
      print('❌ [Service] Erro ao completar missão: $e');
      rethrow;
    }
  }

  /// Busca o progresso do usuário em todas as trilhas
  Future<List<UserPathProgress>> getUserProgress(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/learning-paths/user/progress'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(response.body);
        return jsonList.map((json) => UserPathProgress.fromJson(json)).toList();
      } else {
        throw Exception('Erro ao buscar progresso: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro na requisição: $e');
    }
  }

  /// Busca estatísticas de uma trilha para o usuário
  Future<Map<String, dynamic>> getPathStats(String pathId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/learning-paths/$pathId/stats'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Erro ao buscar estatísticas: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro na requisição: $e');
    }
  }
}
