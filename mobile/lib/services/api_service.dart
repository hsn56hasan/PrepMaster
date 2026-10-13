import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../models/university.dart';
import '../models/question.dart';
import '../models/vocabulary.dart';
import '../models/writing_guide.dart';
import '../models/mistake_item.dart';
import '../models/exam_result.dart';
import '../models/listening_track.dart';
import '../models/essay_evaluation_result.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Smart base URL detection
  String _customBaseUrl = '';

  String get baseUrl {
    if (_customBaseUrl.isNotEmpty) return _customBaseUrl;
    if (kIsWeb) return 'http://127.0.0.1:8050';
    try {
      if (Platform.isAndroid) {
        // Default to Wi-Fi IP for real phones, fallback to 10.0.2.2 for emulator
        return 'http://172.16.1.211:8050';
      }
    } catch (_) {}
    return 'http://127.0.0.1:8050';
  }

  void setBaseUrl(String url) {
    _customBaseUrl = url;
  }

  // --- Universities ---
  Future<List<University>> getUniversities() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/universities')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => University.fromJson(e)).toList();
      }
    } catch (_) {}
    // Fallback to local asset
    final jsonStr = await rootBundle.loadString('assets/data/universities.json');
    final List<dynamic> list = json.decode(jsonStr);
    return list.map((e) => University.fromJson(e)).toList();
  }

  // --- Questions ---
  Future<List<Question>> getQuestions({String? universityId, String? level, String? category}) async {
    try {
      var uri = Uri.parse('$baseUrl/api/questions').replace(queryParameters: {
        if (universityId != null && universityId != 'all') 'university_id': universityId,
        if (level != null && level != 'all') 'level': level,
        if (category != null && category != 'all') 'category': category,
      });
      final res = await http.get(uri).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => Question.fromJson(e)).toList();
      }
    } catch (_) {}

    // Fallback filter over asset questions
    final jsonStr = await rootBundle.loadString('assets/data/questions.json');
    final List<dynamic> list = json.decode(jsonStr);
    var all = list.map((e) => Question.fromJson(e)).toList();

    return all.where((q) {
      if (universityId != null && universityId != 'all') {
        if (q.universityId != universityId && q.universityId != 'general') return false;
      }
      if (level != null && level != 'all') {
        if (q.level.toUpperCase() != level.toUpperCase()) return false;
      }
      if (category != null && category != 'all') {
        if (q.category.toLowerCase() != category.toLowerCase()) return false;
      }
      return true;
    }).toList();
  }

  // --- Vocabulary ---
  Future<List<VocabularyItem>> getVocabulary({String? level, String? search}) async {
    try {
      var uri = Uri.parse('$baseUrl/api/vocabulary').replace(queryParameters: {
        if (level != null && level != 'all') 'level': level,
        if (search != null && search.isNotEmpty) 'search': search,
      });
      final res = await http.get(uri).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => VocabularyItem.fromJson(e)).toList();
      }
    } catch (_) {}

    final jsonStr = await rootBundle.loadString('assets/data/vocabulary.json');
    final List<dynamic> list = json.decode(jsonStr);
    var all = list.map((e) => VocabularyItem.fromJson(e)).toList();

    // Apply local storage status
    final prefs = await SharedPreferences.getInstance();
    for (var v in all) {
      final savedStatus = prefs.getString('vocab_${v.id}');
      if (savedStatus != null) v.status = savedStatus;
    }

    return all.where((v) {
      if (level != null && level != 'all' && v.level.toUpperCase() != level.toUpperCase()) return false;
      if (search != null && search.isNotEmpty) {
        final s = search.toLowerCase();
        if (!v.word.toLowerCase().contains(s) &&
            !v.meaningTr.toLowerCase().contains(s) &&
            !v.definitionEn.toLowerCase().contains(s)) {
          return false;
        }
      }
      return true;
    }).toList();
  }

  Future<void> updateVocabStatus(String wordId, String status) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('vocab_$wordId', status);

    try {
      await http.post(
        Uri.parse('$baseUrl/api/vocabulary/$wordId/status'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'status': status}),
      ).timeout(const Duration(seconds: 2));
    } catch (_) {}
  }

  // --- Writing Guides ---
  Future<List<WritingGuide>> getWritingGuides() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/writing-guides')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => WritingGuide.fromJson(e)).toList();
      }
    } catch (_) {}

    final jsonStr = await rootBundle.loadString('assets/data/writing_guides.json');
    final List<dynamic> list = json.decode(jsonStr);
    return list.map((e) => WritingGuide.fromJson(e)).toList();
  }

  // --- Exam Submit & Mistake Vault ---
  Future<ExamResult> submitExam({
    required String universityId,
    required String level,
    required int durationSeconds,
    required Map<String, String> answers,
    required Map<String, int> questionTimes,
    bool isMistakePractice = false,
  }) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/exam/submit'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'university_id': universityId,
          'level': level,
          'duration_seconds': durationSeconds,
          'answers': answers,
          'question_times': questionTimes,
          'is_mistake_practice': isMistakePractice,
        }),
      ).timeout(const Duration(seconds: 4));

      if (res.statusCode == 200) {
        final data = json.decode(utf8.decode(res.bodyBytes));
        return ExamResult.fromJson(data);
      }
    } catch (_) {}

    // Offline simulation calculation
    final allQuestions = await getQuestions();
    final qMap = {for (var q in allQuestions) q.id: q};

    int correct = 0;
    List<ExamResultDetail> details = [];

    answers.forEach((qId, ans) {
      final q = qMap[qId];
      if (q != null) {
        final isCorrect = (ans == q.correctAnswer);
        if (isCorrect) correct++;
        details.add(ExamResultDetail(
          questionId: qId,
          category: q.category,
          level: q.level,
          questionText: q.question,
          chosenAnswer: ans,
          correctAnswer: q.correctAnswer,
          isCorrect: isCorrect,
          timeSpent: questionTimes[qId] ?? 0,
          explanationTr: q.explanationTr,
          options: q.options,
        ));
      }
    });

    final score = ((correct / (answers.isEmpty ? 1 : answers.length)) * 100).roundToDouble();

    // Save mistakes locally
    final prefs = await SharedPreferences.getInstance();
    List<String> rawMistakes = prefs.getStringList('local_mistakes') ?? [];
    for (var d in details) {
      if (!d.isCorrect) {
        if (!rawMistakes.contains(d.questionId)) rawMistakes.add(d.questionId);
      } else {
        rawMistakes.remove(d.questionId);
      }
    }
    await prefs.setStringList('local_mistakes', rawMistakes);

    return ExamResult(
      attemptId: DateTime.now().millisecondsSinceEpoch,
      score: score,
      totalQuestions: answers.length,
      correctCount: correct,
      wrongCount: answers.length - correct,
      durationSeconds: durationSeconds,
      timeAnalytics: {
        'avg_time_per_question': (durationSeconds / (answers.isEmpty ? 1 : answers.length)).roundToDouble(),
        'time_traps_count': details.where((d) => d.timeSpent >= 90).length,
      },
      details: details,
    );
  }

  // --- Mistake Vault ---
  Future<List<MistakeItem>> getMistakes() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/mistakes')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => MistakeItem.fromJson(e)).toList();
      }
    } catch (_) {}

    // Offline local mistakes
    final prefs = await SharedPreferences.getInstance();
    List<String> localMistakeIds = prefs.getStringList('local_mistakes') ?? [];
    if (localMistakeIds.isEmpty) return [];

    final allQuestions = await getQuestions();
    final qMap = {for (var q in allQuestions) q.id: q};

    List<MistakeItem> list = [];
    for (var id in localMistakeIds) {
      final q = qMap[id];
      if (q != null) {
        list.add(MistakeItem(
          questionId: id,
          universityId: q.universityId,
          level: q.level,
          category: q.category,
          wrongCount: 1,
          lastWrongAnswer: '',
          lastWrongAt: DateTime.now().toIso8601String(),
          questionDetails: q,
        ));
      }
    }
    return list;
  }

  Future<void> resolveMistake(String questionId) async {
    final prefs = await SharedPreferences.getInstance();
    List<String> rawMistakes = prefs.getStringList('local_mistakes') ?? [];
    rawMistakes.remove(questionId);
    await prefs.setStringList('local_mistakes', rawMistakes);

    try {
      await http.post(
        Uri.parse('$baseUrl/api/mistakes/$questionId/resolve'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 2));
    } catch (_) {}
  }

  Future<void> recordMistake({
    required String questionId,
    required String universityId,
    required String level,
    required String category,
    required String wrongAnswer,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    List<String> rawMistakes = prefs.getStringList('local_mistakes') ?? [];
    if (!rawMistakes.contains(questionId)) {
      rawMistakes.add(questionId);
      await prefs.setStringList('local_mistakes', rawMistakes);
    }

    try {
      await http.post(
        Uri.parse('$baseUrl/api/exam/submit'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'university_id': universityId,
          'level': level,
          'duration_seconds': 60,
          'answers': {questionId: wrongAnswer},
        }),
      ).timeout(const Duration(seconds: 2));
    } catch (_) {}
  }

  // --- Dashboard Stats ---
  Future<Map<String, dynamic>> getStats() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/stats')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        return json.decode(utf8.decode(res.bodyBytes));
      }
    } catch (_) {}

    final mistakes = await getMistakes();
    final vocab = await getVocabulary();
    final mastered = vocab.where((v) => v.status == 'mastered').length;

    return {
      'profile': {'streak_days': 1},
      'total_exams_taken': 1,
      'average_exam_score': 65.0,
      'mastered_vocab': mastered,
      'total_vocab': vocab.length,
      'unresolved_mistakes': mistakes.length,
      'recent_exams': [],
    };
  }

  // --- Listening Tracks ---
  Future<List<ListeningTrack>> getListeningTracks({String? universityId, String? level, String? type}) async {
    try {
      var uri = Uri.parse('$baseUrl/api/listening').replace(queryParameters: {
        if (universityId != null && universityId != 'all') 'university_id': universityId,
        if (level != null && level != 'all') 'level': level,
        if (type != null && type != 'all') 'type': type,
      });
      final res = await http.get(uri).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => ListeningTrack.fromJson(e)).toList();
      }
    } catch (_) {}

    // Fallback to local asset
    final jsonStr = await rootBundle.loadString('assets/data/listening.json');
    final List<dynamic> list = json.decode(jsonStr);
    return list.map((e) => ListeningTrack.fromJson(e)).where((item) {
      if (universityId != null && universityId != 'all' && item.universityId != universityId) return false;
      if (level != null && level != 'all' && item.level.toUpperCase() != level.toUpperCase()) return false;
      if (type != null && type != 'all' && item.type != type) return false;
      return true;
    }).toList();
  }

  // --- AI Essay Evaluator ---
  Future<EssayEvaluationResult> evaluateEssay({
    required String essay,
    String? prompt,
    String? universityId,
    String? level,
  }) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/writing/evaluate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'essay': essay,
          'prompt': prompt ?? 'General Academic Essay',
          'university_id': universityId ?? 'itu',
          'level': level ?? 'B2',
        }),
      ).timeout(const Duration(seconds: 5));

      if (res.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(utf8.decode(res.bodyBytes));
        return EssayEvaluationResult.fromJson(data);
      }
    } catch (_) {}

    // Offline Local Evaluator
    return _localEvaluateEssay(essay);
  }

  EssayEvaluationResult _localEvaluateEssay(String text) {
    final clean = text.trim();
    final words = RegExp(r"\b[A-Za-z0-9'-]+\b").allMatches(clean).map((m) => m.group(0)!).toList();
    final wordCount = words.length;

    if (wordCount < 30) {
      return EssayEvaluationResult(
        overallScore: 25,
        estimatedCefr: 'A1/A2',
        isPassing: false,
        wordCount: wordCount,
        paragraphCount: 1,
        avgSentenceLength: wordCount.toDouble(),
        taskAchievementScore: 8,
        coherenceCohesionScore: 6,
        lexicalResourceScore: 6,
        grammaticalRangeScore: 5,
        detectedTransitions: [],
        detectedAcademicWords: [],
        informalWordsFound: [],
        strengthsTr: ['Denemeye başlanmış olması.'],
        improvementsTr: [
          'Giriş, en az 2 gelişme ve 1 sonuç paragrafı oluşturun.',
          'Kelime sayısını en az 250 seviyesine çıkarın.',
          'Fikirlerinizi "For example", "Consequently" gibi bağlaçlarla destekleyin.'
        ],
      );
    }

    final paragraphs = clean.split('\n').map((p) => p.trim()).where((p) => p.isNotEmpty).toList();
    final paraCount = paragraphs.length;

    int taScore = 0;
    if (wordCount >= 250) {
      taScore += 15;
    } else if (wordCount >= 180) {
      taScore += 10;
    } else if (wordCount >= 120) {
      taScore += 6;
    } else {
      taScore += 3;
    }

    if (paraCount >= 3 && paraCount <= 5) {
      taScore += 7;
    } else if (paraCount >= 2) {
      taScore += 4;
    } else {
      taScore += 2;
    }

    final firstPara = paragraphs.isNotEmpty ? paragraphs.first.toLowerCase() : '';
    final hasThesis = ['in my opinion', 'this essay will', 'i believe', 'in my view', 'it is argued', 'firstly', 'two main']
        .any((phrase) => firstPara.contains(phrase));
    if (hasThesis) taScore += 3;
    taScore = taScore.clamp(5, 25);

    final transitionsCatalog = [
      'furthermore', 'moreover', 'in addition', 'additionally', 'consequently',
      'as a result', 'therefore', 'thus', 'on the other hand', 'in contrast',
      'nevertheless', 'nonetheless', 'firstly', 'secondly', 'thirdly',
      'for instance', 'for example', 'to illustrate', 'in conclusion', 'to sum up',
      'in particular', 'specifically', 'subsequently', 'despite', 'although'
    ];
    final textLower = clean.toLowerCase();
    final foundTransitions = transitionsCatalog.where((t) => textLower.contains(t)).toList();
    final ccScore = (foundTransitions.length * 3 + (paraCount >= 3 ? 5 : 0)).clamp(6, 25);

    final academicKeywords = [
      'significant', 'significantly', 'demonstrate', 'illustrate', 'crucial',
      'essential', 'fundamental', 'mitigate', 'phenomenon', 'consequence',
      'substantial', 'implement', 'perspective', 'evident', 'facilitate',
      'comprehensive', 'implication', 'predominant', 'indicate', 'perception',
      'correlation', 'diminish', 'enhance', 'advocate', 'prevalent', 'framework',
      'infrastructure', 'inevitable', 'profound', 'diversity', 'sustainable'
    ];
    final foundAcademic = academicKeywords.where((w) => textLower.contains(w)).toList();

    final informalKeywords = ['a lot of', 'lots of', 'gonna', 'wanna', 'kids', 'stuff', 'thing', 'really good', 'bad', 'huge'];
    final foundInformal = informalKeywords.where((w) => textLower.contains(w)).toList();

    final lexScore = (8 + foundAcademic.length * 2 - foundInformal.length * 2).clamp(6, 25);

    final sentences = clean.split(RegExp(r'[.!?]+')).map((s) => s.trim()).where((s) => s.length > 3).toList();
    final avgSentenceLen = wordCount / (sentences.isNotEmpty ? sentences.length : 1);

    final complexConnectors = ['although', 'whereas', 'while', 'even though', 'since', 'unless', 'provided that', 'because'];
    final foundComplex = complexConnectors.where((c) => textLower.contains(c)).length;

    final passiveMarkers = ['is considered', 'are considered', 'was found', 'were found', 'has been', 'have been', 'is believed', 'can be seen', 'be implemented'];
    final hasPassive = passiveMarkers.where((p) => textLower.contains(p)).length;

    int grammarScore = 10;
    if (avgSentenceLen >= 12 && avgSentenceLen <= 26) grammarScore += 6;
    if (foundComplex >= 2) grammarScore += 5;
    if (hasPassive >= 1) grammarScore += 4;
    grammarScore = grammarScore.clamp(6, 25);

    final overall = taScore + ccScore + lexScore + grammarScore;

    String cefr = 'A2 (Elementary)';
    if (overall >= 85) {
      cefr = 'C1 (Mastery)';
    } else if (overall >= 70) {
      cefr = 'B2 (Vantage - Hazırlık Muafiyet Barajı)';
    } else if (overall >= 55) {
      cefr = 'B1 (Threshold)';
    }

    final strengths = <String>[];
    if (taScore >= 18) strengths.add('Gelişmiş kelime hacmi ($wordCount kelime) ve net kompozisyon yapısı.');
    if (foundTransitions.isNotEmpty) strengths.add('Geçiş bağlaçlarının zengin kullanımı (${foundTransitions.take(4).join(", ")} vb.).');
    if (foundAcademic.isNotEmpty) strengths.add('Akademik kelime dağarcığı kullanımı (${foundAcademic.take(4).join(", ")}).');
    if (foundComplex >= 2) strengths.add('Bileşik ve karmaşık cümle yapıları (complex sentence structures).');
    if (strengths.isEmpty) strengths.add('Temel fikir akışı sağlanmış.');

    final improvements = <String>[];
    if (wordCount < 220) improvements.add('Kelime sayısı hedefin altında ($wordCount/250). Argümanlarınızı genişletin.');
    if (paraCount < 4) improvements.add('Paragraf ayrımını belirginleştirin (Giriş, 2 Gelişme, 1 Sonuç).');
    if (!hasThesis) improvements.add('Giriş paragrafının sonuna açık bir Tez Cümlesi (Thesis Statement) ekleyin.');
    if (foundTransitions.length < 4) improvements.add('Paragraflar arasında "Furthermore", "Consequently" gibi bağlaçlar kullanın.');
    if (foundInformal.isNotEmpty) improvements.add('Resmi olmayan ifadelerden kaçının (${foundInformal.join(", ")} yerine akademik alternatifler seçin).');
    if (improvements.isEmpty) improvements.add('Zaman kiplerini kontrol ederek C2 düzeyine yaklaşabilirsiniz.');

    return EssayEvaluationResult(
      overallScore: overall,
      estimatedCefr: cefr,
      isPassing: overall >= 65,
      wordCount: wordCount,
      paragraphCount: paraCount,
      avgSentenceLength: double.parse(avgSentenceLen.toStringAsFixed(1)),
      taskAchievementScore: taScore,
      coherenceCohesionScore: ccScore,
      lexicalResourceScore: lexScore,
      grammaticalRangeScore: grammarScore,
      detectedTransitions: foundTransitions,
      detectedAcademicWords: foundAcademic,
      informalWordsFound: foundInformal,
      strengthsTr: strengths,
      improvementsTr: improvements,
    );
  }
}
