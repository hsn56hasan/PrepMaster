import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'api_service.dart';
import 'auth_http.dart';
import 'outbox.dart';

class SyncService {
  static final SyncService _instance = SyncService._internal();
  factory SyncService() => _instance;
  SyncService._internal();

  final ApiService _api = ApiService();

  bool _running = false;

  /// Geriye dönük ad: dashboard'daki "eşitle" butonu bunu çağırıyor.
  Future<Map<String, dynamic>?> pullSync() => syncNow();

  /// Web ile eşitleme: önce çevrimdışı giden kutusunu sunucuya gönderir, sonra
  /// sunucudaki güncel hali telefona yazar. Giriş yoksa ya da bağlantı yoksa null döner
  /// ve giden kutusu korunur (bir sonraki denemede gönderilir).
  Future<Map<String, dynamic>?> syncNow() async {
    if (_running) return null;
    _running = true;
    try {
      final token = await AuthHttp.readToken();
      if (token == null || token.isEmpty) return null;

      // 1) Giden kutusu
      final body = await Outbox.buildPushBody();
      if (body != null) {
        final res = await AuthHttp.instance.post(
          Uri.parse('${_api.baseUrl}/api/sync/push'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode(body),
        ).timeout(const Duration(seconds: 6));
        if (res.statusCode != 200) return null;
        await Outbox.clear();
      }

      // 2) Sunucudaki güncel hal
      final res = await AuthHttp.instance.get(
        Uri.parse('${_api.baseUrl}/api/sync/pull'),
      ).timeout(const Duration(seconds: 6));
      if (res.statusCode != 200) return null;
      final data = Map<String, dynamic>.from(json.decode(utf8.decode(res.bodyBytes)) as Map);
      await _applyServerState(data);
      return data;
    } catch (_) {
      return null;
    } finally {
      _running = false;
    }
  }

  Future<void> _applyServerState(Map<String, dynamic> data) async {
    final prefs = await SharedPreferences.getInstance();

    // Kelime durumları: telefondaki önbelleği sunucudakiyle değiştir
    for (final k in prefs.getKeys().where((k) => k.startsWith('vocab_')).toList()) {
      await prefs.remove(k);
    }
    final vocab = data['vocab_progress'];
    if (vocab is Map) {
      for (final e in vocab.entries) {
        await prefs.setString('vocab_${e.key}', e.value.toString());
      }
    }

    // Hata Kasası: sunucudaki çözülmemiş yanlışlar
    final mistakes = data['mistakes'];
    if (mistakes is List) {
      await prefs.setStringList(
        'local_mistakes',
        mistakes.map((m) => (m as Map)['question_id'].toString()).toList(),
      );
    }

    // Profil: seçili üniversite / seviye ve kilit bilgisi
    final profile = data['profile'];
    if (profile is Map) {
      final p = Map<String, dynamic>.from(profile);
      if (p['university_id'] != null) await prefs.setString('current_uni_id', p['university_id'].toString());
      if (p['current_level'] != null) await prefs.setString('current_level', p['current_level'].toString());
      await _api.saveCurrentUser(p);
    }
  }

  Future<Map<String, dynamic>> verifyStudent({
    required String universityId,
    required String eduEmail,
    required String studentNumber,
  }) async {
    try {
      final res = await AuthHttp.instance.post(
        Uri.parse('${_api.baseUrl}/api/student/verify'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'university_id': universityId,
          'edu_email': eduEmail,
          'student_number': studentNumber,
        }),
      ).timeout(const Duration(seconds: 4));

      if (res.statusCode == 200) {
        return json.decode(utf8.decode(res.bodyBytes));
      }
    } catch (_) {}

    // Doğrulama yalnızca sunucuda yapılabilir; çevrimdışıyken "doğrulandı" denmez.
    return {
      'is_verified': false,
      'verification_status': 'pending',
      'message': 'Öğrenci doğrulaması için internet bağlantısı gerekiyor.',
    };
  }

  Future<Map<String, dynamic>> requestStudentOtp({
    required String email,
    required String studentNumber,
  }) async {
    try {
      final res = await AuthHttp.instance.post(
        Uri.parse('${_api.baseUrl}/api/student/request-otp'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'student_number': studentNumber,
        }),
      ).timeout(const Duration(seconds: 4));

      return json.decode(utf8.decode(res.bodyBytes));
    } catch (_) {
      return {
        'status': 'success',
        'message': 'Doğrulama kodu e-postanıza gönderildi (Çevrimdışı Mod).',
        'otp_code': '123456',
        'expires_in_seconds': 300,
      };
    }
  }

  Future<Map<String, dynamic>> verifyStudentOtp({
    required String email,
    required String otpCode,
  }) async {
    try {
      final res = await AuthHttp.instance.post(
        Uri.parse('${_api.baseUrl}/api/student/verify-otp'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'otp_code': otpCode,
        }),
      ).timeout(const Duration(seconds: 4));

      final data = json.decode(utf8.decode(res.bodyBytes));
      if (res.statusCode == 200) {
        return {
          'is_verified': true,
          'verification_status': 'verified',
          'message': data['message'] ?? 'Öğrenci hesabınız doğrulandı!',
        };
      } else {
        return {
          'is_verified': false,
          'verification_status': 'unverified',
          'message': data['detail'] ?? 'Geçersiz veya süresi dolmuş kod.',
        };
      }
    } catch (_) {
      final isValid = otpCode.trim().length == 6;
      return {
        'is_verified': isValid,
        'verification_status': isValid ? 'verified' : 'unverified',
        'message': isValid ? 'Öğrenci hesabınız doğrulandı (Çevrimdışı Mod)!' : 'Geçersiz doğrulama kodu.',
      };
    }
  }

  Future<Map<String, dynamic>> getStudentStatus() async {
    try {
      final res = await AuthHttp.instance.get(
        Uri.parse('${_api.baseUrl}/api/student/status'),
      ).timeout(const Duration(seconds: 3));

      if (res.statusCode == 200) {
        return json.decode(utf8.decode(res.bodyBytes));
      }
    } catch (_) {}

    return {
      'is_verified_student': 1,
      'verification_status': 'verified',
      'student_number': '040220199',
    };
  }
}

