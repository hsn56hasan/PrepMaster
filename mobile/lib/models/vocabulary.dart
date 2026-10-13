class VocabularyItem {
  final String id;
  final String word;
  final String level;
  final String partOfSpeech;
  final String pronunciation;
  final String meaningTr;
  final String definitionEn;
  final List<String> synonyms;
  final List<String> antonyms;
  final String exampleSentence;
  final String collocation;
  String status; // 'learning', 'mastered', 'unreviewed'

  VocabularyItem({
    required this.id,
    required this.word,
    required this.level,
    required this.partOfSpeech,
    required this.pronunciation,
    required this.meaningTr,
    required this.definitionEn,
    required this.synonyms,
    required this.antonyms,
    required this.exampleSentence,
    required this.collocation,
    this.status = 'unreviewed',
  });

  factory VocabularyItem.fromJson(Map<String, dynamic> json) {
    return VocabularyItem(
      id: json['id'] ?? '',
      word: json['word'] ?? '',
      level: json['level'] ?? 'B2',
      partOfSpeech: json['part_of_speech'] ?? '',
      pronunciation: json['pronunciation'] ?? '',
      meaningTr: json['meaning_tr'] ?? '',
      definitionEn: json['definition_en'] ?? '',
      synonyms: (json['synonyms'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      antonyms: (json['antonyms'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      exampleSentence: json['example_sentence'] ?? '',
      collocation: json['collocation'] ?? '',
      status: json['status'] ?? 'unreviewed',
    );
  }
}
