import 'dart:convert';

import 'package:cryptoquest/core/config/app_config.dart';
import 'package:cryptoquest/features/auth/user_profile_model.dart';
import 'package:cryptoquest/features/missions/models/mission_model.dart';
import 'package:cryptoquest/features/quiz/models/quiz_model.dart';
import 'package:http/http.dart' as http;

class MissionApiService {
  /// Busca a lista de missoes diarias para o usuário autenticado
  Future<List<Mission>> getDailyMissions(String token) async {
    final response = await http.get(
      Uri.parse('${AppConfig.baseUrl}/missions/daily'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      },
    );

    if (response.statusCode == 200) {
      // Decodifica a resposta, que eh uma lista de objetos JSON
      final List<dynamic> responseBody = jsonDecode(response.body);
      // Converte cada objeto Json em um Objeto mission e retorna a lista
      return responseBody.map((json) => Mission.fromJson(json)).toList();
    } else {
      throw Exception('Falha ao carregar as missões diárias.');
    }
  }

  Future<Quiz> getQuizById(String token, String quizId) async {
    final response = await http.get(
      Uri.parse('${AppConfig.baseUrl}/quizzes/$quizId'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      },
    );

    if (response.statusCode == 200) {
      // Decodifica a resposta, que eh uma lista de objetos JSON
      return Quiz.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Falha ao carregar o conteúdo do quiz.');
    }
  }

  Future<UserProfile> completeQuizMissions(
    String token, String missionId, List<int> answers) async {
    final response = await http.post(
      Uri.parse('${AppConfig.baseUrl}/missions/$missionId/complete'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      },
      body: jsonEncode({"answers" : answers}),  
    );

    if (response.statusCode == 200) {
      // Decodifica a resposta, que eh uma lista de objetos JSON
      return UserProfile.fromJson(jsonDecode(response.body));
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception('Falha ao completar a missão: ${errorData['detail']}');
    }
  }
}
