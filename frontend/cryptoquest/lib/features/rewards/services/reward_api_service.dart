import 'dart:convert';
import 'package:cryptoquest/core/config/app_config.dart';
import 'package:cryptoquest/features/rewards/models/reward_model.dart';
import 'package:http/http.dart' as http;

class RewardApiService {
  static const String baseUrl = AppConfig.baseUrl;

  Future<List<UserReward>> getUserRewardsHistory(
      String userId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/rewards/user/$userId/history'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = jsonDecode(response.body);
        return jsonList.map((json) => UserReward.fromJson(json)).toList();
      } else {
        throw Exception(
            'Falha ao carregar histórico de recompensas: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar histórico de recompensas: $e');
    }
  }

  Future<List<UserBadge>> getUserBadges(String userId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/rewards/user/$userId/badges'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = jsonDecode(response.body);
        return jsonList.map((json) => UserBadge.fromJson(json)).toList();
      } else {
        throw Exception('Falha ao carregar badges: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar badges: $e');
    }
  }

  Future<List<Badge>> getAvailableBadges(String userId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/rewards/user/$userId/available-badges'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = jsonDecode(response.body);
        return jsonList.map((json) => Badge.fromJson(json)).toList();
      } else {
        throw Exception(
            'Falha ao carregar badges disponíveis: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar badges disponíveis: $e');
    }
  }

  Future<List<Badge>> getAllBadges(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/rewards/badges'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = jsonDecode(response.body);
        return jsonList.map((json) => Badge.fromJson(json)).toList();
      } else {
        throw Exception(
            'Falha ao carregar badges disponíveis: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao buscar badges disponíveis: $e');
    }
  }

  Future<Map<String, dynamic>> awardMissionCompletion(
    String userId,
    String missionId,
    double score,
    String missionType,
    String token,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/rewards/award/mission'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'user_id': userId,
          'mission_id': missionId,
          'score': score,
          'mission_type': missionType,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception(
            'Falha ao conceder recompensas: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro ao conceder recompensas: $e');
    }
  }
}
