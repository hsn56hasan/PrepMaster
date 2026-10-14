class SpeakingTask {
  final String id;
  final String universityId;
  final String targetUniversity;
  final String level;
  final String title;
  final String topic;
  final int prepTimeSeconds;
  final int speakTimeSeconds;
  final String instructionsTr;
  final String promptEn;
  final List<String> guidingQuestions;
  final List<String> keyVocabulary;
  final String modelAnswerTranscript;

  SpeakingTask({
    required this.id,
    required this.universityId,
    required this.targetUniversity,
    required this.level,
    required this.title,
    required this.topic,
    required this.prepTimeSeconds,
    required this.speakTimeSeconds,
    required this.instructionsTr,
    required this.promptEn,
    required this.guidingQuestions,
    required this.keyVocabulary,
    required this.modelAnswerTranscript,
  });

  factory SpeakingTask.fromJson(Map<String, dynamic> json) {
    return SpeakingTask(
      id: json['id'] ?? '',
      universityId: json['university_id'] ?? 'general',
      targetUniversity: json['target_university'] ?? '',
      level: json['level'] ?? 'B2',
      title: json['title'] ?? '',
      topic: json['topic'] ?? '',
      prepTimeSeconds: json['prep_time_seconds'] ?? 45,
      speakTimeSeconds: json['speak_time_seconds'] ?? 90,
      instructionsTr: json['instructions_tr'] ?? '',
      promptEn: json['prompt_en'] ?? '',
      guidingQuestions: (json['guiding_questions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      keyVocabulary: (json['key_vocabulary'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      modelAnswerTranscript: json['model_answer_transcript'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'university_id': universityId,
        'target_university': targetUniversity,
        'level': level,
        'title': title,
        'topic': topic,
        'prep_time_seconds': prepTimeSeconds,
        'speak_time_seconds': speakTimeSeconds,
        'instructions_tr': instructionsTr,
        'prompt_en': promptEn,
        'guiding_questions': guidingQuestions,
        'key_vocabulary': keyVocabulary,
        'model_answer_transcript': modelAnswerTranscript,
      };
}
