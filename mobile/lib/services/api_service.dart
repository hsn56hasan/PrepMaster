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
import '../models/speaking_task.dart';
import '../models/speaking_evaluation_result.dart';

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
        return 'http://10.247.49.48:8050';
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
  Future<List<WritingGuide>> getWritingGuides({String? level}) async {
    final query = level != null && level.isNotEmpty && level != 'all' ? '?level=$level' : '';
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/writing-guides$query')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
        return list.map((e) => WritingGuide.fromJson(e)).toList();
      }
    } catch (_) {}

    final jsonStr = await rootBundle.loadString('assets/data/writing_guides.json');
    final List<dynamic> list = json.decode(jsonStr);
    var filtered = list;
    if (level != null && level.isNotEmpty && level != 'all') {
      final target = level.toUpperCase();
      final matched = list.where((e) => (e['level'] as String? ?? '').toUpperCase() == target).toList();
      if (matched.isNotEmpty) {
        filtered = matched;
      }
    }
    return filtered.map((e) => WritingGuide.fromJson(e)).toList();
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

  // --- Speaking Tasks & Offline Evaluator ---
  Future<List<SpeakingTask>> getSpeakingTasks({String? universityId, String? level}) async {
    final queryParams = <String>[];
    if (universityId != null && universityId.isNotEmpty && universityId != 'all') {
      queryParams.add('university_id=$universityId');
    }
    if (level != null && level.isNotEmpty && level != 'all') {
      queryParams.add('level=$level');
    }
    final queryString = queryParams.isNotEmpty ? '?${queryParams.join('&')}' : '';

    try {
      final res = await http.get(Uri.parse('$baseUrl/api/speaking$queryString')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(res.bodyBytes));
        return data.map((e) => SpeakingTask.fromJson(e)).toList();
      }
    } catch (_) {}

    // Offline asset fallback
    try {
      final jsonStr = await rootBundle.loadString('assets/data/speaking.json');
      final List<dynamic> data = json.decode(jsonStr);
      var filtered = data;
      if (level != null && level.isNotEmpty && level != 'all') {
        final target = level.toUpperCase();
        final matched = data.where((e) => (e['level'] as String? ?? '').toUpperCase() == target).toList();
        if (matched.isNotEmpty) {
          filtered = matched;
        }
      }
      return filtered.map((e) => SpeakingTask.fromJson(e)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<SpeakingEvaluationResult> evaluateSpeaking({
    required String transcript,
    required String taskId,
    required int durationSeconds,
  }) async {
    // Try backend evaluation
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/speaking/evaluate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'transcript': transcript,
          'task_id': taskId,
          'duration_seconds': durationSeconds,
        }),
      ).timeout(const Duration(seconds: 4));

      if (res.statusCode == 200) {
        final data = json.decode(utf8.decode(res.bodyBytes));
        return SpeakingEvaluationResult.fromJson(data);
      }
    } catch (_) {}

    // Offline smart speech evaluator fallback
    final words = RegExp(r"\b[A-Za-z']+\b").allMatches(transcript).map((m) => m.group(0)!).toList();
    final wordCount = words.length;
    final duration = durationSeconds > 15 ? durationSeconds : 60;
    final wpm = double.parse(((wordCount / duration) * 60).toStringAsFixed(1));
    final textLower = transcript.toLowerCase();

    int fluencyScore = 14;
    if (wpm >= 100 && wpm <= 160) {
      fluencyScore = 23;
    } else if (wpm >= 80) {
      fluencyScore = 19;
    }

    final academicKeywords = [
      'fundamental', 'significant', 'mitigate', 'consequently', 'furthermore',
      'paradigm', 'infrastructure', 'mobility', 'autonomy', 'subsidize',
      'intermittency', 'biodiversity', 'unprecedented', 'catalyze', 'sustainable'
    ];
    final foundAcademic = academicKeywords.where((w) => textLower.contains(w)).toList();
    final lexicalScore = (10 + foundAcademic.length * 3).clamp(8, 25);

    final connectors = ['although', 'because', 'while', 'furthermore', 'however', 'therefore', 'for instance'];
    final foundConnectors = connectors.where((c) => textLower.contains(c)).toList();
    final grammarScore = (10 + foundConnectors.length * 3).clamp(8, 25);

    final taskScore = (12 + (wordCount >= 70 ? 8 : 4)).clamp(8, 25);
    final overall = fluencyScore + lexicalScore + grammarScore + taskScore;

    String cefr = 'A2 (Developing)';
    if (overall >= 85) {
      cefr = 'C1 (Advanced Fluency)';
    } else if (overall >= 70) {
      cefr = 'B2 (Vantage - Muafiyet Yeterli)';
    } else if (overall >= 55) {
      cefr = 'B1 (Independent)';
    }

    final strengths = <String>[];
    if (fluencyScore >= 20) {
      strengths.add('Akıcı konuşma temposu ($wpm kelime/dk) sınav standartlarına çok uygun.');
    } else {
      strengths.add('Konuşma akışı temel düzeyde tamamlandı.');
    }
    if (foundAcademic.isNotEmpty) {
      strengths.add('Akademik kelime kullanımı (${foundAcademic.take(3).join(", ")}).');
    }

    final improvements = <String>[];
    if (wpm < 100) {
      improvements.add('Konuşma temponuz $wpm WPM. İdeal hazırlık temposu 110-150 WPM aralığıdır.');
    }
    if (foundAcademic.length < 2) {
      improvements.add('Akademik bağlaçlar ve konuya özgü terimler kullanmaya çalışın.');
    }

    return SpeakingEvaluationResult(
      wordCount: wordCount,
      speakingRateWpm: wpm,
      overallScore: overall,
      cefrLevel: cefr,
      isPassing: overall >= 65,
      fluencyScore: fluencyScore,
      lexicalScore: lexicalScore,
      grammaticalScore: grammarScore,
      taskScore: taskScore,
      detectedAcademicWords: foundAcademic,
      detectedTransitions: foundConnectors,
      strengthsTr: strengths,
      improvementsTr: improvements,
      modelTranscript: 'Sample model answer with fluent academic delivery.',
    );
  }

  // --- Full Mock Exam ---
  Future<Map<String, dynamic>> getMockExam(String universityId, {String? level}) async {
    final query = level != null && level.isNotEmpty && level != 'all' ? '?level=$level' : '';
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/exam/mock/$universityId$query')).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(utf8.decode(res.bodyBytes));
        if (data['sections'] != null && data['sections']['multiple_choice'] != null) {
          final List<dynamic> qList = data['sections']['multiple_choice'];
          data['parsed_questions'] = qList.map((e) => Question.fromJson(e)).toList();
        }
        return data;
      }
    } catch (_) {}

    final allQuestions = await getQuestions(universityId: universityId, level: level);
    return {
      'exam_title': 'Resmi Muafiyet Deneme Sınavı',
      'duration_minutes': 120,
      'passing_score': 60,
      'parsed_questions': allQuestions.take(15).toList(),
    };
  }

  // --- Student Summary Report Card ---
  Future<Map<String, dynamic>> getReportSummary() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/report/summary')).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return json.decode(utf8.decode(res.bodyBytes));
      }
    } catch (_) {}

    final stats = await getStats();
    final mistakes = await getMistakes();
    final vocab = await getVocabulary();
    final mastered = vocab.where((v) => v.status == 'mastered').length;

    return {
      'student_profile': {
        'student_number': '040220199',
        'is_verified_student': 1,
      },
      'target_university': {
        'name': 'Üniversite Hazırlık Programı',
      },
      'readiness_status': mistakes.length <= 5 ? 'Muafiyete Hazır' : 'Geliştirilmeli (Eksikler Var)',
      'readiness_color': mistakes.length <= 5 ? 'emerald' : 'amber',
      'average_score': stats['average_exam_score'] ?? 65.0,
      'passing_score': 60,
      'total_exams_taken': stats['total_exams_taken'] ?? 1,
      'unresolved_mistakes_count': mistakes.length,
      'mistakes_by_category': <String, dynamic>{},
      'mastered_vocabulary_count': mastered,
      'total_vocabulary_count': vocab.length,
      'generated_at': DateTime.now().toString().substring(0, 16),
    };
  }

  // --- User Authentication & Session Management ---
  Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
  }) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'identifier': identifier,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 4));

      final data = json.decode(utf8.decode(res.bodyBytes));
      if (res.statusCode == 200 && data['status'] == 'success') {
        final user = data['user'];
        await saveCurrentUser(user);
        return {'success': true, 'user': user};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Giriş başarısız.'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Bağlantı hatası: ${e.toString()}'};
    }
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String username,
    required String password,
    required String fullName,
    String? universityId,
    String? studentNumber,
  }) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'username': username,
          'password': password,
          'full_name': fullName,
          'university_id': universityId ?? 'itu',
          'student_number': studentNumber ?? '',
        }),
      ).timeout(const Duration(seconds: 4));

      final data = json.decode(utf8.decode(res.bodyBytes));
      if (res.statusCode == 200 && data['status'] == 'success') {
        final user = data['user'];
        await saveCurrentUser(user);
        return {'success': true, 'user': user};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Kayıt başarısız.'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Bağlantı hatası: ${e.toString()}'};
    }
  }

  Future<Map<String, dynamic>?> getCurrentUser({int userId = 1}) async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/auth/me?user_id=$userId')).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final user = json.decode(utf8.decode(res.bodyBytes));
        await saveCurrentUser(user);
        return user;
      }
    } catch (_) {}
    return await loadSavedUser();
  }

  Future<void> saveCurrentUser(Map<String, dynamic> user) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_user_data', json.encode(user));
      if (user['unlocked_universities'] is List) {
        final list = (user['unlocked_universities'] as List).map((e) => e.toString()).toList();
        await prefs.setStringList('unlocked_universities', list);
      }
      if (user['university_id'] != null) {
        await prefs.setString('current_uni_id', user['university_id'].toString());
      }
      if (user['verified_university'] != null) {
        await prefs.setString('verified_university', user['verified_university'].toString());
      }
    } catch (_) {}
  }

  Future<Map<String, dynamic>?> loadSavedUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final str = prefs.getString('auth_user_data');
      if (str != null) {
        return json.decode(str) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  Future<void> clearSavedUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_user_data');
      await prefs.remove('unlocked_universities');
      await prefs.remove('verified_university');
    } catch (_) {}
  }

  // --- Student Document Scanning & Verification ---
  Future<Map<String, dynamic>> scanStudentDocument({
    String? documentText,
    String? sampleKey,
    int userId = 1,
  }) async {
    try {
      final Map<String, dynamic> body = {'user_id': userId};
      if (documentText != null) body['document_text'] = documentText;
      if (sampleKey != null) body['sample_key'] = sampleKey;

      final res = await http.post(
        Uri.parse('$baseUrl/api/student/scan-document'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(body),
      ).timeout(const Duration(seconds: 10));

      final data = json.decode(utf8.decode(res.bodyBytes));
      if (res.statusCode == 200) {
        final matchedUni = data['matched_university_id']?.toString() ?? 'itu';
        final user = await loadSavedUser() ?? <String, dynamic>{'id': userId, 'username': 'student'};
        user['verified_university'] = matchedUni;
        user['university_id'] = matchedUni;
        user['is_verified_student'] = 1;
        user['verification_status'] = 'verified';
        List<dynamic> unlocked = data['unlocked_universities'] ?? [matchedUni, 'general'];
        if (!unlocked.contains(matchedUni)) unlocked.add(matchedUni);
        user['unlocked_universities'] = unlocked;
        await saveCurrentUser(user);

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('current_uni_id', matchedUni);
        await prefs.setString('verified_university', matchedUni);
        await prefs.setStringList('unlocked_universities', unlocked.map((e) => e.toString()).toList());

        return {'success': true, ...data};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Belge doğrulanamadı.'};
      }
    } catch (_) {}

    // Offline simulation fallback
    String detected = sampleKey ?? 'itu';
    if (documentText != null && documentText.isNotEmpty) {
      final t = documentText.toLowerCase();
      if (t.contains('hacettepe')) {
        detected = 'hacettepe';
      } else if (t.contains('ankara')) {
        detected = 'ankara';
      } else if (t.contains('gazi')) {
        detected = 'gazi';
      } else if (t.contains('ege')) {
        detected = 'ege';
      } else if (t.contains('koç') || t.contains('koc')) {
        detected = 'koc';
      } else if (t.contains('sabancı') || t.contains('sabanci')) {
        detected = 'sabanci';
      } else if (t.contains('boğaziçi') || t.contains('bogazici') || t.contains('boun')) {
        detected = 'boun';
      } else if (t.contains('orta doğu') || t.contains('odtu') || t.contains('metu')) {
        detected = 'metu';
      } else if (t.contains('itu') || t.contains('istanbul teknik')) {
        detected = 'itu';
      }
    }

    final barcode = 'EDEVLET-${detected.toUpperCase()}-2026';
    final user = await loadSavedUser() ?? <String, dynamic>{'id': userId, 'username': 'student'};
    user['verified_university'] = detected;
    user['university_id'] = detected;
    user['is_verified_student'] = 1;
    user['verification_status'] = 'verified';
    List<dynamic> unlocked = user['unlocked_universities'] is List
        ? List.from(user['unlocked_universities'])
        : ['general'];
    if (!unlocked.contains(detected)) unlocked.add(detected);
    user['unlocked_universities'] = unlocked;
    await saveCurrentUser(user);

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('current_uni_id', detected);
      await prefs.setString('verified_university', detected);
      await prefs.setStringList('unlocked_universities', unlocked.map((e) => e.toString()).toList());
    } catch (_) {}

    return {
      'success': true,
      'status': 'success',
      'matched_university_id': detected,
      'matched_university_name': detected.toUpperCase(),
      'student_number': '221049102',
      'document_barcode': barcode,
      'is_active_student': true,
      'unlocked_universities': unlocked,
      'message': 'Belgeniz başarıyla tarandı ve onaylandı.',
    };
  }

  // --- 50 TL University Membership Paywall & 3D Secure ---
  Future<Map<String, dynamic>> initiate3DSecurePayment({
    required String universityId,
    String cardHolder = 'Ahmet Yılmaz',
    String cardNumber = '5528 7900 0000 0001',
    String expireMonth = '12',
    String expireYear = '28',
    String cvv = '123',
    double amountTry = 50.0,
    int userId = 1,
  }) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/membership/3d-init'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': userId,
          'university_id': universityId,
          'card_holder': cardHolder,
          'card_number': cardNumber,
          'expire_month': expireMonth,
          'expire_year': expireYear,
          'cvv': cvv,
          'amount_try': amountTry,
        }),
      ).timeout(const Duration(seconds: 5));

      if (res.statusCode == 200) {
        final data = json.decode(utf8.decode(res.bodyBytes));
        return {'success': true, ...data};
      }
    } catch (_) {}

    // Offline simulation fallback
    return {
      'success': true,
      'status': 'success',
      'session_id': '3DS-${DateTime.now().millisecondsSinceEpoch}',
      'masked_phone': '+90 5** *** ** 84',
      'sms_code_sandbox': '123456',
      'expires_in_seconds': 180,
      'amount_try': 50.0,
      'currency': 'TRY',
    };
  }

  Future<Map<String, dynamic>> unlockUniversityMembership({
    required String universityId,
    String cardHolder = 'Öğrenci',
    String cardNumber = '4242 4242 4242 4242',
    String? sessionId,
    String? smsCode,
    int userId = 1,
  }) async {
    try {
      final Map<String, dynamic> body = {
        'user_id': userId,
        'university_id': universityId,
        'card_holder': cardHolder,
        'card_number': cardNumber,
      };
      if (sessionId != null) body['session_id'] = sessionId;
      if (smsCode != null) body['sms_code'] = smsCode;

      final res = await http.post(
        Uri.parse('$baseUrl/api/membership/unlock'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(body),
      ).timeout(const Duration(seconds: 10));

      final data = json.decode(utf8.decode(res.bodyBytes));
      if (res.statusCode == 200) {
        final user = await loadSavedUser();
        List<dynamic> unlockedList = data['unlocked_universities'] ?? [];
        if (!unlockedList.contains(universityId)) {
          unlockedList.add(universityId);
        }
        if (user != null) {
          user['unlocked_universities'] = unlockedList;
          await saveCurrentUser(user);
        }
        final prefs = await SharedPreferences.getInstance();
        await prefs.setStringList('unlocked_universities', unlockedList.map((e) => e.toString()).toList());

        return {'success': true, ...data};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Ödeme alınamadı.'};
      }
    } catch (_) {}

    // Offline simulation fallback
    const double grossAmount = 50.00;
    const double vatRate = 0.20;
    final double netAmount = double.parse((grossAmount / (1.0 + vatRate)).toStringAsFixed(2));
    final double vatAmount = double.parse((grossAmount - netAmount).toStringAsFixed(2));
    final receiptNo = 'EARSIV-2026-${(1000 + DateTime.now().millisecondsSinceEpoch % 9000)}';

    final user = await loadSavedUser();
    List<dynamic> unlockedList = [];
    if (user != null && user['unlocked_universities'] is List) {
      unlockedList = List.from(user['unlocked_universities']);
    }
    if (!unlockedList.contains(universityId)) {
      unlockedList.add(universityId);
    }
    if (user != null) {
      user['unlocked_universities'] = unlockedList;
      await saveCurrentUser(user);
    }
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('unlocked_universities', unlockedList.map((e) => e.toString()).toList());
    } catch (_) {}

    final cleanCard = cardNumber.replaceAll(' ', '');
    final lastFour = cleanCard.length >= 4 ? cleanCard.substring(cleanCard.length - 4) : '0001';

    return {
      'success': true,
      'status': 'success',
      'message': 'Ödeme onaylandı ve üniversite erişimi açıldı.',
      'unlocked_university': universityId,
      'university_id': universityId,
      'unlocked_universities': unlockedList,
      'price_try': grossAmount,
      'reference': receiptNo,
      'invoice_number': receiptNo,
      'receipt': {
        'receipt_no': receiptNo,
        'gross_amount': grossAmount,
        'vat_rate': vatRate,
        'vat_amount': vatAmount,
        'net_amount': netAmount,
        'currency': 'TRY',
        'payment_date': DateTime.now().toIso8601String(),
        'card_last_four': lastFour,
      },
    };
  }

  Future<bool> checkUniversityAccess({
    required String universityId,
    int userId = 1,
  }) async {
    if (universityId == 'general' || universityId == 'all') return true;

    // 1. Check local session state first
    final user = await loadSavedUser();
    if (user != null) {
      if (user['verified_university'] == universityId ||
          user['university_id'] == universityId) {
        return true;
      }
      final unlocked = user['unlocked_universities'];
      if (unlocked is List && unlocked.contains(universityId)) {
        return true;
      }
    }

    try {
      final prefs = await SharedPreferences.getInstance();
      final localUnlocked = prefs.getStringList('unlocked_universities');
      if (localUnlocked != null && localUnlocked.contains(universityId)) {
        return true;
      }
      final verifiedUni = prefs.getString('verified_university');
      if (verifiedUni == universityId) {
        return true;
      }
      // If user has not loaded any user profile yet, check current_uni_id fallback
      if (user == null) {
        final currentUniId = prefs.getString('current_uni_id');
        if (currentUniId == universityId) {
          return true;
        }
      }
    } catch (_) {}

    // 2. Try remote backend check
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/api/membership/check?university_id=$universityId&user_id=$userId'),
      ).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        final data = json.decode(utf8.decode(res.bodyBytes));
        return data['has_access'] == true;
      }
    } catch (_) {}

    return false;
  }
}



