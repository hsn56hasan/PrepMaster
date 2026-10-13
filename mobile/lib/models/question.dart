class QuestionOption {
  final String key;
  final String text;

  QuestionOption({required this.key, required this.text});

  factory QuestionOption.fromJson(Map<String, dynamic> json) {
    return QuestionOption(
      key: json['key'] ?? '',
      text: json['text'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {'key': key, 'text': text};
}

class Question {
  final String id;
  final String universityId;
  final String level;
  final String category;
  final String? passage;
  final String question;
  final List<QuestionOption> options;
  final String correctAnswer;
  final String explanationTr;
  final String? explanationEn;

  Question({
    required this.id,
    required this.universityId,
    required this.level,
    required this.category,
    this.passage,
    required this.question,
    required this.options,
    required this.correctAnswer,
    required this.explanationTr,
    this.explanationEn,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['id'] ?? '',
      universityId: json['university_id'] ?? 'general',
      level: json['level'] ?? 'B2',
      category: json['category'] ?? 'General',
      passage: json['passage'],
      question: json['question'] ?? '',
      options: (json['options'] as List<dynamic>?)
              ?.map((e) => QuestionOption.fromJson(e))
              .toList() ??
          [],
      correctAnswer: json['correct_answer'] ?? '',
      explanationTr: json['explanation_tr'] ?? '',
      explanationEn: json['explanation_en'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'university_id': universityId,
        'level': level,
        'category': category,
        if (passage != null) 'passage': passage,
        'question': question,
        'options': options.map((e) => e.toJson()).toList(),
        'correct_answer': correctAnswer,
        'explanation_tr': explanationTr,
        if (explanationEn != null) 'explanation_en': explanationEn,
      };
}
