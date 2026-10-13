class University {
  final String id;
  final String name;
  final String shortName;
  final String examName;
  final int passingScore;
  final int durationMinutes;
  final int totalQuestions;
  final String badgeColor;
  final String description;
  final List<ExamSection> sections;
  final List<String> tips;

  University({
    required this.id,
    required this.name,
    required this.shortName,
    required this.examName,
    required this.passingScore,
    required this.durationMinutes,
    required this.totalQuestions,
    required this.badgeColor,
    required this.description,
    required this.sections,
    required this.tips,
  });

  factory University.fromJson(Map<String, dynamic> json) {
    return University(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      shortName: json['short_name'] ?? '',
      examName: json['exam_name'] ?? '',
      passingScore: json['passing_score'] ?? 60,
      durationMinutes: json['duration_minutes'] ?? 120,
      totalQuestions: json['total_questions'] ?? 50,
      badgeColor: json['badge_color'] ?? 'blue',
      description: json['description'] ?? '',
      sections: (json['sections'] as List<dynamic>?)
              ?.map((e) => ExamSection.fromJson(e))
              .toList() ??
          [],
      tips: (json['tips'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

class ExamSection {
  final String name;
  final int questionsCount;
  final int weightPercent;
  final String description;

  ExamSection({
    required this.name,
    required this.questionsCount,
    required this.weightPercent,
    required this.description,
  });

  factory ExamSection.fromJson(Map<String, dynamic> json) {
    return ExamSection(
      name: json['name'] ?? '',
      questionsCount: json['questions_count'] ?? 0,
      weightPercent: json['weight_percent'] ?? 0,
      description: json['description'] ?? '',
    );
  }
}
