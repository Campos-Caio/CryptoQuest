import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:cryptoquest/core/config/app_config.dart';

class AIService {
  static const String _baseUrl = AppConfig.baseUrl;

  /// Busca o perfil de IA do usuário
  static Future<Map<String, dynamic>?> getUserAIProfile(
      String userId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/ai/profile/$userId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data'];
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Busca recomendações personalizadas do usuário
  static Future<List<Map<String, dynamic>>> getUserRecommendations(
      String userId, String token,
      {int limit = 5}) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/ai/recommendations/$userId?limit=$limit'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  /// Busca insights de IA do usuário
  static Future<Map<String, dynamic>?> getUserInsights(
      String userId, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/ai/insights/$userId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data'];
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Busca recomendações de learning paths (fallback para recomendações de IA)
  static Future<List<Map<String, dynamic>>> getLearningPathRecommendations(
      String userId, String token,
      {int limit = 5}) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/learning-paths/recommended?limit=$limit'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  /// Busca sugestão de dificuldade para um domínio específico
  static Future<Map<String, dynamic>?> getDifficultySuggestion(
      String userId, String domain, String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/ai/difficulty-suggestion/$userId?domain=$domain'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data'];
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Busca sugestões de conteúdo para um domínio específico
  static Future<List<Map<String, dynamic>>> getContentSuggestions(
      String userId, String domain, String token,
      {int limit = 3}) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$_baseUrl/ai/content-suggestions/$userId?domain=$domain&limit=$limit'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  /// Busca métricas dos modelos de IA (para administradores)
  static Future<Map<String, dynamic>?> getAIModelMetrics(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/ai/model-metrics'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data'];
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Verifica se a IA está habilitada e funcionando
  static Future<bool> isAIEnabled(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/ai/model-metrics'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
