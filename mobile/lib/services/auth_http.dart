import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Sunucu, kullanıcı kimliğini YALNIZCA `Authorization: Bearer <token>` başlığından alır;
/// istek gövdesindeki/sorgudaki `user_id` yok sayılır. Bu istemci, giriş sırasında
/// kaydedilen oturum token'ını her isteğe ekler.
class AuthHttp extends http.BaseClient {
  AuthHttp._();
  static final AuthHttp instance = AuthHttp._();

  static const String tokenKey = 'auth_token';
  final http.Client _inner = http.Client();

  static Future<void> saveToken(String? token) async {
    final prefs = await SharedPreferences.getInstance();
    if (token == null || token.isEmpty) {
      await prefs.remove(tokenKey);
    } else {
      await prefs.setString(tokenKey, token);
    }
  }

  static Future<String?> readToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(tokenKey);
  }

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    try {
      final token = await readToken();
      if (token != null && token.isNotEmpty && !request.headers.containsKey('Authorization')) {
        request.headers['Authorization'] = 'Bearer $token';
      }
    } catch (_) {}
    return _inner.send(request);
  }
}
