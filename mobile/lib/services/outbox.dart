import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// Çevrimdışı giden kutusu.
///
/// Sunucu öğrencinin verisinin tek gerçek kaynağıdır; web ve mobil aynı veriyi görür.
/// Telefon internetsizken yapılan değişiklikler (kelime durumu, yeni yanlış, çözülen
/// hata, sınav sonucu, seviye/üniversite seçimi) burada birikir. Bağlantı gelince
/// [SyncService.syncNow] önce bunları sunucuya gönderir, sonra sunucudaki güncel hali
/// çeker. Böylece web'de çözülen bir hata telefonda "geri dirilmez": telefon yalnızca
/// KENDİ yaptığı değişiklikleri gönderir, eski önbelleğini değil.
class Outbox {
  static const _vocabKey = 'outbox_vocab';
  static const _mistakesKey = 'outbox_mistakes';
  static const _resolvedKey = 'outbox_resolved';
  static const _examsKey = 'outbox_exams';
  static const _profileKey = 'outbox_profile';

  static const allKeys = [_vocabKey, _mistakesKey, _resolvedKey, _examsKey, _profileKey];

  static Future<void> addVocab(String wordId, String status) async {
    final prefs = await SharedPreferences.getInstance();
    final map = _decodeMap(prefs.getString(_vocabKey));
    map[wordId] = status;
    await prefs.setString(_vocabKey, json.encode(map));
  }

  static Future<void> addMistake(Map<String, dynamic> mistake) async {
    final prefs = await SharedPreferences.getInstance();
    final list = _decodeList(prefs.getString(_mistakesKey));
    list.add({...mistake, 'last_wrong_at': DateTime.now().toUtc().toIso8601String().substring(0, 19).replaceFirst('T', ' ')});
    await prefs.setString(_mistakesKey, json.encode(list));
    // Aynı soru daha önce çevrimdışı "çözüldü" diye işaretlendiyse o işaret geçersiz.
    final resolved = prefs.getStringList(_resolvedKey) ?? [];
    if (resolved.remove(mistake['question_id'])) {
      await prefs.setStringList(_resolvedKey, resolved);
    }
  }

  static Future<void> addResolved(String questionId) async {
    final prefs = await SharedPreferences.getInstance();
    final resolved = prefs.getStringList(_resolvedKey) ?? [];
    if (!resolved.contains(questionId)) {
      resolved.add(questionId);
      await prefs.setStringList(_resolvedKey, resolved);
    }
  }

  static Future<void> addExamAttempt(Map<String, dynamic> attempt) async {
    final prefs = await SharedPreferences.getInstance();
    final list = _decodeList(prefs.getString(_examsKey));
    list.add({...attempt, 'created_at': DateTime.now().toUtc().toIso8601String().substring(0, 19)});
    await prefs.setString(_examsKey, json.encode(list));
  }

  static Future<void> setProfile(String universityId, String level) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_profileKey, json.encode({'university_id': universityId, 'current_level': level}));
  }

  /// Sunucuya gidecek gövde; giden kutusu boşsa null.
  static Future<Map<String, dynamic>?> buildPushBody() async {
    final prefs = await SharedPreferences.getInstance();
    final vocab = _decodeMap(prefs.getString(_vocabKey));
    final mistakes = _decodeList(prefs.getString(_mistakesKey));
    final resolved = prefs.getStringList(_resolvedKey) ?? [];
    final exams = _decodeList(prefs.getString(_examsKey));
    final profileRaw = prefs.getString(_profileKey);
    if (vocab.isEmpty && mistakes.isEmpty && resolved.isEmpty && exams.isEmpty && profileRaw == null) {
      return null;
    }
    return {
      if (profileRaw != null) 'profile': json.decode(profileRaw),
      if (mistakes.isNotEmpty) 'mistakes': mistakes,
      if (resolved.isNotEmpty) 'resolved_mistakes': resolved,
      if (vocab.isNotEmpty) 'vocab_progress': vocab,
      if (exams.isNotEmpty) 'exam_attempts': exams,
    };
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    for (final k in allKeys) {
      await prefs.remove(k);
    }
  }

  static Map<String, dynamic> _decodeMap(String? raw) {
    if (raw == null) return {};
    try {
      return Map<String, dynamic>.from(json.decode(raw) as Map);
    } catch (_) {
      return {};
    }
  }

  static List<Map<String, dynamic>> _decodeList(String? raw) {
    if (raw == null) return [];
    try {
      return (json.decode(raw) as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
    } catch (_) {
      return [];
    }
  }
}
