class SpeakingEvaluationResult {
  final int wordCount;
  final double speakingRateWpm;
  final int overallScore;
  final String cefrLevel;
  final bool isPassing;
  final int fluencyScore;
  final int lexicalScore;
  final int grammaticalScore;
  final int taskScore;
  final List<String> detectedAcademicWords;
  final List<String> detectedTransitions;
  final List<String> strengthsTr;
  final List<String> improvementsTr;
  final String modelTranscript;

  SpeakingEvaluationResult({
    required this.wordCount,
    required this.speakingRateWpm,
    required this.overallScore,
    required this.cefrLevel,
    required this.isPassing,
    required this.fluencyScore,
    required this.lexicalScore,
    required this.grammaticalScore,
    required this.taskScore,
    required this.detectedAcademicWords,
    required this.detectedTransitions,
    required this.strengthsTr,
    required this.improvementsTr,
    required this.modelTranscript,
  });

  factory SpeakingEvaluationResult.fromJson(Map<String, dynamic> json) {
    final scores = json['scores'] as Map<String, dynamic>? ?? {};
    return SpeakingEvaluationResult(
      wordCount: json['word_count'] ?? 0,
      speakingRateWpm: (json['speaking_rate_wpm'] as num?)?.toDouble() ?? 0.0,
      overallScore: json['overall_score'] ?? 0,
      cefrLevel: json['cefr_level'] ?? 'B2',
      isPassing: json['is_passing'] ?? false,
      fluencyScore: scores['fluency_and_coherence'] ?? 15,
      lexicalScore: scores['lexical_resource'] ?? 15,
      grammaticalScore: scores['grammatical_range'] ?? 15,
      taskScore: scores['task_achievement'] ?? 15,
      detectedAcademicWords: (json['detected_academic_words'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
      detectedTransitions: (json['detected_transitions'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
      strengthsTr: (json['strengths_tr'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
      improvementsTr: (json['improvements_tr'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
      modelTranscript: json['model_transcript'] ?? '',
    );
  }
}
