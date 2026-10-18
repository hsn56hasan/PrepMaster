class WritingSection {
  final String section;
  final List<String> elements;

  WritingSection({required this.section, required this.elements});

  factory WritingSection.fromJson(Map<String, dynamic> json) {
    return WritingSection(
      section: json['section'] ?? '',
      elements: (json['elements'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

class WritingGuide {
  final String id;
  final String title;
  final String description;
  final List<WritingSection> structure;
  final List<String> keyTransitions;
  final String sampleTopic;
  final String? bandScoreTip;
  final String? modelEssay;
  final int? modelBandScore;
  final List<String> annotatedStrengths;
  final List<String> commonPitfalls;

  WritingGuide({
    required this.id,
    required this.title,
    required this.description,
    required this.structure,
    required this.keyTransitions,
    required this.sampleTopic,
    this.bandScoreTip,
    this.modelEssay,
    this.modelBandScore,
    this.annotatedStrengths = const [],
    this.commonPitfalls = const [],
  });

  factory WritingGuide.fromJson(Map<String, dynamic> json) {
    return WritingGuide(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      structure: (json['structure'] as List<dynamic>?)
              ?.map((e) => WritingSection.fromJson(e))
              .toList() ??
          [],
      keyTransitions: (json['key_transitions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      sampleTopic: json['sample_topic'] ?? '',
      bandScoreTip: json['band_score_tip'],
      modelEssay: json['model_essay'],
      modelBandScore: json['model_band_score'],
      annotatedStrengths: (json['annotated_strengths'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      commonPitfalls: (json['common_pitfalls'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}
