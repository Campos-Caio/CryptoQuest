import 'dart:convert';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/quiz/models/quiz_model.dart';
import 'package:http/http.dart' as http;
import '../../../core/config/app_config.dart';

class MissionApiService {
  static String baseUrl = AppConfig.baseUrl;

  // Buscar missões elegíveis filtradas por nível e status de conclusão
  Future<List<Mission>> getDailyMissions(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/missions/daily'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> missionsJson = json.decode(response.body);
        return missionsJson.map((json) => Mission.fromJson(json)).toList();
      } else {
        throw Exception('Falha ao carregar missões: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  // Buscar quiz específico
  Future<Quiz> getQuiz(String quizId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/quizzes/$quizId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final quizJson = json.decode(response.body);
        return Quiz.fromJson(quizJson);
      } else {
        throw Exception('Falha ao carregar quiz: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }

  // Completar missão
  Future<Map<String, dynamic>> completeMission(
      String missionId, List<int> answers, String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/missions/$missionId/complete'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'answers': answers,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        // Capturar o corpo da resposta para obter a mensagem de erro
        final errorBody = json.decode(response.body);
        final errorMessage = errorBody['detail'] ?? 'Erro desconhecido';
        throw Exception('$errorMessage (${response.statusCode})');
      }
    } catch (e) {
      // Se já é uma Exception com mensagem de erro, re-throw
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Erro de conexão: $e');
    }
  }
}
