import 'package:cryptoquest/features/initial_questionnaire/models/question_model.dart';
import 'package:cryptoquest/services/questionnaire_api_service.dart';
import 'package:flutter/material.dart';

class UserAnswer {
  final String questionId;
  final String selectedOptionId;

  UserAnswer({required this.questionId, required this.selectedOptionId});
}

class QuestionnaireProvider extends ChangeNotifier {
  final QuestionnaireApiService _apiService = QuestionnaireApiService();

  bool isLoading = false;
  String? errorMessage;
  InitialQuestionnaire? quesitonnaire;

  final List<UserAnswer> _userAnswers = [];
  List<UserAnswer> get userAnswers => _userAnswers;

  // Carrega as perguntas do backend
  Future<void> fetchQuestionnaire(String token) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      quesitonnaire = await _apiService.getInitialQuestionnaire(token);
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
  Future<bool> submitAllAnswers(String token) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    // Monta o corpo da requisicao conforme o esperado pela API
    final submission = {
      'answers': _userAnswers.map((answer) => {
            'question_id': answer.questionId,
            'selected_option_id': answer.selectedOptionId
          }).toList(), 
    };

    try{
      await _apiService.submitAnswers(token, submission); 
      return true;
    } catch (error){
      errorMessage = error.toString();
      return false;
    } finally{
      isLoading = false;
      notifyListeners();
    }
  }
}
