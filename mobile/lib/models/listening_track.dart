class ListeningOption {
  final String key;
  final String text;

  ListeningOption({required this.key, required this.text});

  factory ListeningOption.fromJson(Map<String, dynamic> json) {
    return ListeningOption(
      key: json['key'] ?? '',
      text: json['text'] ?? '',
    );
  }
}

class ListeningQuestion {
  final String id;
  final String question;
  final List<ListeningOption> options;
  final String correctAnswer;
  final String explanationTr;

  ListeningQuestion({
    required this.id,
    required this.question,
    required this.options,
    required this.correctAnswer,
    required this.explanationTr,
  });

  factory ListeningQuestion.fromJson(Map<String, dynamic> json) {
    var rawOpts = json['options'] as List? ?? [];
    return ListeningQuestion(
      id: json['id'] ?? '',
      question: json['question'] ?? '',
      options: rawOpts.map((o) => ListeningOption.fromJson(o)).toList(),
      correctAnswer: json['correct_answer'] ?? '',
      explanationTr: json['explanation_tr'] ?? '',
    );
  }
}

class ListeningTrack {
  final String id;
  final String universityId;
  final String level;
  final String type; // "note_taking" or "while_listening"
  final String title;
  final String subtitle;
  final String targetUniversity;
  final int durationMinutes;
  final int lectureDurationSeconds;
  final String instructionsTr;
  final String audioScript;
  final List<String> suggestedNotesTr;
  final List<ListeningQuestion> questions;

  ListeningTrack({
    required this.id,
    required this.universityId,
    required this.level,
    required this.type,
    required this.title,
    required this.subtitle,
    required this.targetUniversity,
    required this.durationMinutes,
    required this.lectureDurationSeconds,
    required this.instructionsTr,
    required this.audioScript,
    required this.suggestedNotesTr,
    required this.questions,
  });

  factory ListeningTrack.fromJson(Map<String, dynamic> json) {
    var rawQuestions = json['questions'] as List? ?? [];
    var rawNotes = json['suggested_notes_tr'] as List? ?? [];

    return ListeningTrack(
      id: json['id'] ?? '',
      universityId: json['university_id'] ?? '',
      level: json['level'] ?? '',
      type: json['type'] ?? 'while_listening',
      title: json['title'] ?? '',
      subtitle: json['subtitle'] ?? '',
      targetUniversity: json['target_university'] ?? '',
      durationMinutes: json['duration_minutes'] ?? 10,
      lectureDurationSeconds: json['lecture_duration_seconds'] ?? 90,
      instructionsTr: json['instructions_tr'] ?? '',
      audioScript: json['audio_script'] ?? '',
      suggestedNotesTr: rawNotes.map((n) => n.toString()).toList(),
      questions: rawQuestions.map((q) => ListeningQuestion.fromJson(q)).toList(),
    );
  }
}
