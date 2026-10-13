class EssayEvaluationResult {
  final int overallScore;
  final String estimatedCefr;
  final bool isPassing;
  final int wordCount;
  final int paragraphCount;
  final double avgSentenceLength;
  final int taskAchievementScore;
  final int coherenceCohesionScore;
  final int lexicalResourceScore;
  final int grammaticalRangeScore;
  final List<String> detectedTransitions;
  final List<String> detectedAcademicWords;
  final List<String> informalWordsFound;
  final List<String> strengthsTr;
  final List<String> improvementsTr;

  EssayEvaluationResult({
    required this.overallScore,
    required this.estimatedCefr,
    required this.isPassing,
    required this.wordCount,
    required this.paragraphCount,
    required this.avgSentenceLength,
    required this.taskAchievementScore,
    required this.coherenceCohesionScore,
    required this.lexicalResourceScore,
    required this.grammaticalRangeScore,
    required this.detectedTransitions,
    required this.detectedAcademicWords,
    required this.informalWordsFound,
    required this.strengthsTr,
    required this.improvementsTr,
  });

  factory EssayEvaluationResult.fromJson(Map<String, dynamic> json) {
    return EssayEvaluationResult(
      overallScore: json['overall_score'] ?? 0,
      estimatedCefr: json['estimated_cefr'] ?? 'B2',
      isPassing: json['is_passing'] ?? false,
      wordCount: json['word_count'] ?? 0,
      paragraphCount: json['paragraph_count'] ?? 0,
      avgSentenceLength: (json['avg_sentence_length'] as num?)?.toDouble() ?? 0.0,
      taskAchievementScore: json['task_achievement_score'] ?? 0,
      coherenceCohesionScore: json['coherence_cohesion_score'] ?? 0,
      lexicalResourceScore: json['lexical_resource_score'] ?? 0,
      grammaticalRangeScore: json['grammatical_range_score'] ?? 0,
      detectedTransitions: (json['detected_transitions'] as List? ?? []).map((e) => e.toString()).toList(),
      detectedAcademicWords: (json['detected_academic_words'] as List? ?? []).map((e) => e.toString()).toList(),
      informalWordsFound: (json['informal_words_found'] as List? ?? []).map((e) => e.toString()).toList(),
      strengthsTr: (json['strengths_tr'] as List? ?? []).map((e) => e.toString()).toList(),
      improvementsTr: (json['improvements_tr'] as List? ?? []).map((e) => e.toString()).toList(),
    );
  }
}
