import 'dart:convert';
import 'package:cryptoquest/core/config/app_config.dart';
import 'package:cryptoquest/features/initial_questionnaire/models/question_model.dart';
import 'package:http/http.dart' as http;

class QuestionnaireApiService {
  Future<InitialQuestionnaire> getInitialQuestionnaire(String token) async {
    final response = await http.get(
      Uri.parse('${AppConfig.baseUrl}/questionnaire/initial'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return InitialQuestionnaire.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Falha ao carregar o questionario!');
    }
  }

  Future<void> submitAnswers(
      String token, Map<String, dynamic> submission) async {
    final response = await http.post(
      Uri.parse('${AppConfig.baseUrl}/questionnaire/initial/submit'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(submission),
    );

    if (response.statusCode != 201) {
      throw Exception('Falha ao enviar as respostas!'); 
    }
  }
}
