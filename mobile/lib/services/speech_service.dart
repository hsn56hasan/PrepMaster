import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// Kelime ve cümleleri İngilizce sesli okur.
///
/// Telefonun yerleşik metin okuma motorunu kullanır: ses dosyası indirmez, ücretli servis
/// gerektirmez, internet yokken de çalışır. Telefonda İngilizce ses paketi yoksa
/// [speak] false döner; arayüz kullanıcıya bunu söyler.
class SpeechService {
  SpeechService._();
  static final SpeechService instance = SpeechService._();

  /// Testler gerçek motor yerine bunu kullanır.
  @visibleForTesting
  static Future<bool> Function(String text, {required bool slow})?
  debugOverride;

  /// Şu an okunan metin (düğmenin "çalıyor" görünümü için).
  final ValueNotifier<String?> speaking = ValueNotifier<String?>(null);

  FlutterTts? _tts;
  bool? _englishAvailable;

  Future<FlutterTts> _engine() async {
    if (_tts != null) return _tts!;
    final tts = FlutterTts();
    try {
      await tts.awaitSpeakCompletion(true);
      // Önce ABD, yoksa İngiltere İngilizcesi
      for (final lang in const ['en-US', 'en-GB']) {
        final ok = await tts.isLanguageAvailable(lang);
        if (ok == true) {
          await tts.setLanguage(lang);
          _englishAvailable = true;
          break;
        }
      }
      _englishAvailable ??= false;
      await tts.setVolume(1.0);
      await tts.setPitch(1.0);
      tts.setCompletionHandler(() => speaking.value = null);
      tts.setCancelHandler(() => speaking.value = null);
      tts.setErrorHandler((_) => speaking.value = null);
    } catch (_) {
      _englishAvailable = false;
    }
    _tts = tts;
    return tts;
  }

  /// Metni okur. [slow] true ise telaffuzu dinlemek için yavaş okur.
  /// Başarısız olursa (ses paketi/motor yok) false döner.
  Future<bool> speak(String text, {bool slow = false}) async {
    final clean = text.trim();
    if (clean.isEmpty) return false;
    final override = debugOverride;
    if (override != null) return override(clean, slow: slow);
    try {
      final tts = await _engine();
      if (_englishAvailable == false && !kIsWeb) return false;
      await tts.stop();
      // flutter_tts hızı: Android'de 0.5 normal konuşma hızıdır
      await tts.setSpeechRate(slow ? 0.25 : 0.45);
      speaking.value = clean;
      final result = await tts.speak(clean);
      if (result != 1 && !kIsWeb) {
        speaking.value = null;
        return false;
      }
      return true;
    } catch (_) {
      speaking.value = null;
      return false;
    }
  }

  Future<void> stop() async {
    speaking.value = null;
    if (debugOverride != null) return;
    try {
      await _tts?.stop();
    } catch (_) {}
  }
}
