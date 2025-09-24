import 'dart:convert';
import 'package:cryptoquest/core/config/app_config.dart';
import 'package:cryptoquest/features/ranking/models/ranking_model.dart';
import 'package:http/http.dart' as http;

class RankingApiService {
  static const String baseUrl = AppConfig.baseUrl;

  Future<Ranking> getGlobalRanking(String token, {int limit = 100}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ranking/global?limit=$limit'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return Ranking.fromJson(jsonDecode(response.body));
      } else {
        throw Exception(
            'Falha ao carregar ranking global: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar ranking global: $e');
    }
  }

  Future<Ranking> getWeeklyRanking(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ranking/weekly'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return Ranking.fromJson(jsonDecode(response.body));
      } else {
        throw Exception(
            'Falha ao carregar ranking semanal: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar ranking semanal: $e');
    }
  }

  Future<UserRankingStats> getUserRankingStats(
      String userId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ranking/user/$userId/stats'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return UserRankingStats.fromJson(jsonDecode(response.body));
      } else {
        throw Exception(
            'Falha ao carregar estatísticas de ranking: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar estatísticas de ranking: $e');
    }
  }
}
