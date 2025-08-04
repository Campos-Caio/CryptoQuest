class QuestionOption {
  final String id;
  final String text;
  final int score;

  QuestionOption({
    required this.id,
    required this.text,
    required this.score,
  });

  factory QuestionOption.fromJson(Map<String, dynamic> json) {
    return QuestionOption(
      id: json["id"],
      text: json["text"],
      score: json["score"],
    );
  }
}

class Question {
  final String id;
  final String text;
  final List<QuestionOption> options;

  Question({required this.id, required this.options, required this.text});

  factory Question.fromJson(Map<String, dynamic> json) {
    var optionsList = json['options'] as List;
    List<QuestionOption> options =
        optionsList.map((i) => QuestionOption.fromJson(i)).toList();
    return Question(
      id: json['id'],
      text: json['text'],
      options: options,
    );
  }
}

class InitialQuestionnaire {
  final String title;
  final List<Question> questions;

  InitialQuestionnaire({required this.questions, required this.title});

  factory InitialQuestionnaire.fromJson(Map<String, dynamic> json) {
    var questionsList = json['questions'] as List;
    List<Question> questions =
        questionsList.map((i) => Question.fromJson(i)).toList();
    return InitialQuestionnaire(questions: questions, title: json['title']);
  }
}
