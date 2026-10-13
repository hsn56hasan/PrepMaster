import 'question.dart';

class MistakeItem {
  final String questionId;
  final String universityId;
  final String level;
  final String category;
  final int wrongCount;
  final String lastWrongAnswer;
  final String lastWrongAt;
  final Question questionDetails;

  MistakeItem({
    required this.questionId,
    required this.universityId,
    required this.level,
    required this.category,
    required this.wrongCount,
    required this.lastWrongAnswer,
    required this.lastWrongAt,
    required this.questionDetails,
  });

  factory MistakeItem.fromJson(Map<String, dynamic> json) {
    return MistakeItem(
      questionId: json['question_id'] ?? '',
      universityId: json['university_id'] ?? 'general',
      level: json['level'] ?? 'B2',
      category: json['category'] ?? 'General',
      wrongCount: json['wrong_count'] ?? 1,
      lastWrongAnswer: json['last_wrong_answer'] ?? '',
      lastWrongAt: json['last_wrong_at'] ?? '',
      questionDetails: Question.fromJson(json['question_details'] ?? {}),
    );
  }
}
