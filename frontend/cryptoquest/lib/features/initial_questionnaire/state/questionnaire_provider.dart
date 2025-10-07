import 'package:cryptoquest/features/initial_questionnaire/models/question_model.dart';
import 'package:cryptoquest/features/initial_questionnaire/services/questionnaire_api_service.dart';
import 'package:flutter/material.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';

class UserAnswer {
  final String questionId;
  final String selectedOptionId;

  UserAnswer({required this.questionId, required this.selectedOptionId});
}

class QuestionnaireProvider extends ChangeNotifier {
  final QuestionnaireApiService _apiService = QuestionnaireApiService();
  late final AuthNotifier authNotifier;
  QuestionnaireProvider({required this.authNotifier});

  bool isLoading = false;
  String? errorMessage;
  InitialQuestionnaire? questionnaire;
  final List<UserAnswer> _userAnswers = [];
  List<UserAnswer> get userAnswers => _userAnswers;

  // Carrega as perguntas do backend
  Future<void> fetchQuestionnaire() async {
    final token = authNotifier.token;

    if (token == null) {
      errorMessage = 'Usuario nao autenticado!';
      notifyListeners();
      return;
    }

    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      questionnaire = await _apiService.getInitialQuestionnaire(token);
    } catch (error) {
      errorMessage = error.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  void addAnswer(String questionId, String optionId) {
    // Remove respostas anteriores para a mesma pergunta se houver
    _userAnswers.removeWhere((answer) => answer.questionId == questionId);
    _userAnswers
        .add(UserAnswer(questionId: questionId, selectedOptionId: optionId));
    notifyListeners();
  }

  // Envia todas as respostas para o backend
  Future<bool> submitAllAnswers() async {
    // Pega o token mais recente do AuthNotifier no momento da submissão
    final token = authNotifier.token;
    if (token == null) {
      errorMessage = "Usuário não autenticado.";
      notifyListeners();
      return false;
    }

    isLoading = true;
    errorMessage = null;
    notifyListeners();

    // Monta o corpo da requisicao conforme o esperado pela API
    final submission = {
      'answers': _userAnswers
          .map((answer) => {
                'question_id': answer.questionId,
                'selected_option_id': answer.selectedOptionId
              })
          .toList(),
    };

    try {
      await _apiService.submitAnswers(token, submission);
      return true;
    } catch (error) {
      errorMessage = error.toString();
      return false;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
