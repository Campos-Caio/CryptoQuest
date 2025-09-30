class Quiz {
  final String id;
  final String title;
  final List<QuizQuestion> questions;

  Quiz({
    required this.id,
    required this.title,
    required this.questions,
  });

  factory Quiz.fromJson(Map<String, dynamic> json) {
    return Quiz(
      id: json['_id'] ?? json['id'] ?? '',
      title: json['title'] ?? '',
      questions: (json['questions'] as List?)
          ?.map((q) => QuizQuestion.fromJson(q))
          .toList() ?? [],
    );
  }
}

class QuizQuestion {
  final String text;
  final List<QuizOption> options;
  final int correctAnswerIndex;

  QuizQuestion({
    required this.text,
    required this.options,
    required this.correctAnswerIndex,
  });

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    return QuizQuestion(
      text: json['text'] ?? '',
      options: (json['options'] as List?)  
          ?.map((option) => QuizOption.fromJson(option))
          .toList() ?? [],
      correctAnswerIndex: json['correct_answer_index'] ?? 0,
    );
  }
}

class QuizOption {
  final String text;

  QuizOption({
    required this.text,
  });

  factory QuizOption.fromJson(Map<String, dynamic> json) {
    return QuizOption(
      text: json['text'] ?? '',
    );
  }
}
