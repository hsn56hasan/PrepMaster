import 'dart:convert';
import 'dart:typed_data';

import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:http/http.dart' as http;

import 'api_service.dart';
import 'auth_http.dart';

/// Writing için yüklenebilen dosya türleri: yalnızca fotoğraf (JPG, PNG, WEBP) veya PDF.
enum EssayFileKind { image, pdf }

class EssayImportException implements Exception {
  EssayImportException(this.message);
  final String message;
  @override
  String toString() => message;
}

/// Essay'i fotoğraftan (telefonda, ML Kit ile) ya da PDF'ten (sunucuda) metne çevirir.
class EssayImportService {
  static const int maxBytes = 10 * 1024 * 1024;
  static const String onlyPhotoOrPdf = 'Yalnızca fotoğraf (JPG, PNG, WEBP) veya PDF yükleyebilirsiniz.';
  static const List<String> allowedExtensions = ['jpg', 'jpeg', 'png', 'webp', 'pdf'];

  /// Dosya türünü uzantıya değil ilk baytlara bakarak belirler.
  static EssayFileKind? detectKind(Uint8List head) {
    bool ascii(int from, String s) {
      if (head.length < from + s.length) return false;
      for (var i = 0; i < s.length; i++) {
        if (head[from + i] != s.codeUnitAt(i)) return false;
      }
      return true;
    }

    if (ascii(0, '%PDF-')) return EssayFileKind.pdf;
    if (head.length >= 3 && head[0] == 0xFF && head[1] == 0xD8 && head[2] == 0xFF) return EssayFileKind.image;
    if (head.isNotEmpty && head[0] == 0x89 && ascii(1, 'PNG')) return EssayFileKind.image;
    if (ascii(0, 'RIFF') && ascii(8, 'WEBP')) return EssayFileKind.image;
    return null;
  }

  static int countWords(String text) => RegExp(r"\b[A-Za-z0-9'-]+\b").allMatches(text).length;

  static String tidy(String text) => text
      .replaceAll('\r\n', '\n')
      .replaceAll('\r', '\n')
      .replaceAll(RegExp(r'[ \t]+\n'), '\n')
      .replaceAll(RegExp(r'\n{3,}'), '\n\n')
      .trim();

  /// Fotoğraftaki yazıyı cihazda okur; fotoğraf sunucuya gönderilmez.
  static Future<String> recognizeImage(String path) async {
    final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
    try {
      final result = await recognizer.processImage(InputImage.fromFilePath(path));
      final text = tidy(result.blocks.map((b) => b.text).join('\n\n'));
      if (countWords(text) < 5) {
        throw EssayImportException(
          'Fotoğrafta okunabilir İngilizce metin bulunamadı. Daha net, düz ve iyi ışıklı bir fotoğraf deneyin.',
        );
      }
      return text;
    } finally {
      await recognizer.close();
    }
  }

  /// PDF'teki metni sunucuda çıkarır (dosya sunucuda saklanmaz).
  static Future<String> extractPdf(Uint8List bytes, String filename) async {
    final req = http.MultipartRequest('POST', Uri.parse('${ApiService().baseUrl}/api/writing/extract-pdf'))
      ..files.add(http.MultipartFile.fromBytes('file', bytes, filename: filename));
    http.Response res;
    try {
      res = await http.Response.fromStream(
        await AuthHttp.instance.send(req).timeout(const Duration(seconds: 30)),
      );
    } catch (_) {
      throw EssayImportException('Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edin.');
    }
    Map<String, dynamic> body = {};
    try {
      body = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    } catch (_) {}
    if (res.statusCode == 401) throw EssayImportException('PDF yüklemek için giriş yapmalısınız.');
    if (res.statusCode != 200) {
      final detail = body['detail'];
      throw EssayImportException(detail is String ? detail : 'PDF okunamadı.');
    }
    return tidy((body['text'] ?? '').toString());
  }
}
