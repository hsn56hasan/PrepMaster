import 'question.dart';

class ExamResultDetail {
  final String questionId;
  final String category;
  final String level;
  final String questionText;
  final String chosenAnswer;
  final String correctAnswer;
  final bool isCorrect;
  final int timeSpent;
  final String explanationTr;
  final List<QuestionOption> options;

  ExamResultDetail({
    required this.questionId,
    required this.category,
    required this.level,
    required this.questionText,
    required this.chosenAnswer,
    required this.correctAnswer,
    required this.isCorrect,
    required this.timeSpent,
    required this.explanationTr,
    required this.options,
  });

  factory ExamResultDetail.fromJson(Map<String, dynamic> json) {
    return ExamResultDetail(
      questionId: json['question_id'] ?? '',
      category: json['category'] ?? 'General',
      level: json['level'] ?? 'B2',
      questionText: json['question_text'] ?? '',
      chosenAnswer: json['chosen_answer'] ?? '',
      correctAnswer: json['correct_answer'] ?? '',
      isCorrect: json['is_correct'] ?? false,
      timeSpent: json['time_spent'] ?? 0,
      explanationTr: json['explanation_tr'] ?? '',
      options: (json['options'] as List<dynamic>?)
              ?.map((e) => QuestionOption.fromJson(e))
              .toList() ??
          [],
    );
  }
}

class ExamResult {
  final int attemptId;
  final double score;
  final int totalQuestions;
  final int correctCount;
  final int wrongCount;
  final int durationSeconds;
  final Map<String, dynamic> timeAnalytics;
  final List<ExamResultDetail> details;

  ExamResult({
    required this.attemptId,
    required this.score,
    required this.totalQuestions,
    required this.correctCount,
    required this.wrongCount,
    required this.durationSeconds,
    required this.timeAnalytics,
    required this.details,
  });

  factory ExamResult.fromJson(Map<String, dynamic> json) {
    return ExamResult(
      attemptId: json['attempt_id'] ?? 0,
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      totalQuestions: json['total_questions'] ?? 0,
      correctCount: json['correct_count'] ?? 0,
      wrongCount: json['wrong_count'] ?? 0,
      durationSeconds: json['duration_seconds'] ?? 0,
      timeAnalytics: json['time_analytics'] ?? {},
      details: (json['details'] as List<dynamic>?)
              ?.map((e) => ExamResultDetail.fromJson(e))
              .toList() ??
          [],
    );
  }
}
