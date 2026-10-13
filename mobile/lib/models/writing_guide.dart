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

  WritingGuide({
    required this.id,
    required this.title,
    required this.description,
    required this.structure,
    required this.keyTransitions,
    required this.sampleTopic,
    this.bandScoreTip,
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
    );
  }
}
