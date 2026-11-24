import 'dart:convert';
import 'dart:math';

import 'package:flutter/services.dart' show rootBundle;

import '../models/question.dart';

const List<String> placementLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

/// Bir kurdaki seviye tespit sonucu.
class PlacementLevelResult {
  final String level;
  int correct = 0;
  int answered = 0;

  /// null: bu kura gelinmedi.
  bool? passed;

  PlacementLevelResult(this.level);
}

/// Uyarlamalı seviye tespit sınavı.
///
/// A1'den başlar; her kurda en fazla [perLevel] soru sorulur. [passMark] doğruya
/// ulaşan kur geçilmiş sayılır ve bir üst kura geçilir. Kurda geçme ihtimali
/// kalmayınca (ikinci yanlış) sınav biter. Böylece en fazla 24, çoğu zaman çok
/// daha az soru sorulur.
class PlacementEngine {
  static const int perLevel = 4;
  static const int passMark = 3;

  final Map<String, List<Question>> _queues = {};
  final Map<String, PlacementLevelResult> results = {
    for (final l in placementLevels) l: PlacementLevelResult(l),
  };
  int _levelIndex = 0;
  int _questionIndex = 0;
  bool _finished = false;

  PlacementEngine(Map<String, List<Question>> pool, {Random? random}) {
    final rnd = random ?? Random();
    for (final lvl in placementLevels) {
      final list = List<Question>.of(pool[lvl] ?? const [])..shuffle(rnd);
      _queues[lvl] = list.take(perLevel).toList();
    }
    _skipEmptyLevels();
  }

  bool get isFinished => _finished;

  String get currentLevel => placementLevels[_levelIndex];

  Question? get current =>
      _finished ? null : _queues[currentLevel]![_questionIndex];

  int get answeredCount => results.values.fold(0, (s, r) => s + r.answered);

  int get correctCount => results.values.fold(0, (s, r) => s + r.correct);

  int get maxQuestions => _queues.values.fold(0, (s, q) => s + q.length);

  /// Geçilen en yüksek kur; hiç geçilemediyse null.
  String? get masteredLevel {
    String? best;
    for (final l in placementLevels) {
      if (results[l]!.passed == true) best = l;
    }
    return best;
  }

  /// Çalışılması önerilen kur: geçilen en yüksek kurun bir üstü (C2'de C2).
  String get recommendedLevel {
    final m = masteredLevel;
    if (m == null) return placementLevels.first;
    final i = placementLevels.indexOf(m);
    return placementLevels[min(i + 1, placementLevels.length - 1)];
  }

  /// Cevabı işler; doğruysa true döner.
  bool answer(String key) {
    final q = current;
    if (q == null) return false;
    final r = results[currentLevel]!;
    final ok = key == q.correctAnswer;
    r.answered++;
    if (ok) r.correct++;

    final total = _queues[currentLevel]!.length;
    final need = min(passMark, total);
    final wrong = r.answered - r.correct;
    if (r.correct >= need) {
      r.passed = true;
      _nextLevel();
    } else if (wrong > total - need) {
      r.passed = false;
      _finished = true;
    } else {
      _questionIndex++;
    }
    return ok;
  }

  void _nextLevel() {
    _levelIndex++;
    _questionIndex = 0;
    _skipEmptyLevels();
  }

  void _skipEmptyLevels() {
    while (_levelIndex < placementLevels.length &&
        _queues[placementLevels[_levelIndex]]!.isEmpty) {
      _levelIndex++;
    }
    if (_levelIndex >= placementLevels.length) {
      _levelIndex = placementLevels.length - 1;
      _finished = true;
    }
  }

  /// Uygulamayla gelen genel havuzdan (özgün q-orj soruları) okuma parçası
  /// gerektirmeyen soruları kurlara göre yükler. İnternet gerektirmez.
  static Future<Map<String, List<Question>>> loadPool() async {
    final raw = await rootBundle.loadString('assets/data/questions.json');
    final list = (json.decode(raw) as List<dynamic>).map(
      (e) => Question.fromJson(e as Map<String, dynamic>),
    );
    final pool = <String, List<Question>>{
      for (final l in placementLevels) l: [],
    };
    for (final q in list) {
      final passage = q.passage;
      if (!q.id.startsWith('q-orj-') ||
          (passage != null && passage.isNotEmpty)) {
        continue;
      }
      if (q.options.length != 4) continue;
      pool[q.level.toUpperCase()]?.add(q);
    }
    return pool;
  }
}
