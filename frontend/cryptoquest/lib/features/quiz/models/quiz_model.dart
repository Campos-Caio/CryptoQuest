import 'dart:convert';

class QuizOption {
  final String text;
  QuizOption({required this.text});

  factory QuizOption.fromJson(Map<String, dynamic> json) {
    return QuizOption(text: json["text"] ?? '');
  }
}

class QuizQuestion {
  final String text;
  final List<QuizOption> options;
  final int correctAnswerIndex;

  QuizQuestion(
      {required this.text,
      required this.correctAnswerIndex,
      required this.options});

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    var optionsList = (json['options'] as List).cast<String>();
    // Convertendo a lista de strings para uma lista de QuizOption
    List<QuizOption> parsedOptions =
        optionsList.map((text) => QuizOption(text: text)).toList();

    return QuizQuestion(
      text: json['text'] ?? 'Pergunta sem texto',
      options: parsedOptions,
      correctAnswerIndex: json['correct_answer_index'] ?? 0,
    );
  }
}

class Quiz {
  final String id;
  final String title;
  final List<QuizQuestion> questions;

  Quiz({required this.id, required this.questions, required this.title});

  factory Quiz.fromJson(Map<String, dynamic> json) {
    var questionsList = (json['questions'] as List);
    List<QuizQuestion> parsedQuestions =
        questionsList.map((q) => QuizQuestion.fromJson(q)).toList();

    return Quiz(
        id: json["_id"] ?? "ID desconhecido!",
        title: json["title"] ?? "Quiz sem titulo",
        questions: parsedQuestions);
  }
}
