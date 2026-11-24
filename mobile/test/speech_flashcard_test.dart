// Kelime kartlarında sesli okuma: Dinle / Yavaş / örnek cümle düğmeleri ve ses paketi yok uyarısı.
// Not: uygulamanın ortak ağ istemcisi testler arasında yeniden kurulamadığı için senaryolar tek testte.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/screens/flashcards_screen.dart';
import 'package:prep_master/services/speech_service.dart';

Future<void> settle(WidgetTester t) async {
  for (var i = 0; i < 8; i++) {
    await t.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 150)));
    await t.pump(const Duration(seconds: 1));
  }
}

void main() {
  testWidgets('Kelime kartı sesli okuma', (t) async {
    SharedPreferences.setMockInitialValues({});
    final calls = <String>[];
    var engineOk = true;
    SpeechService.debugOverride = (text, {required bool slow}) async {
      calls.add('${slow ? "yavas" : "normal"}:$text');
      return engineOk;
    };
    addTearDown(() => SpeechService.debugOverride = null);

    t.view.physicalSize = const Size(720, 1480);
    t.view.devicePixelRatio = 2.0;
    addTearDown(t.view.reset);
    await t.pumpWidget(const MaterialApp(home: FlashcardsScreen(currentLevel: 'B2')));
    for (var i = 0; i < 30 && find.byKey(const Key('tts_word')).evaluate().isEmpty; i++) {
      await settle(t);
    }
    final word = t.widgetList<Text>(find.byType(Text)).firstWhere((w) => w.style?.fontSize == 34).data!;

    // 1) Ön yüz: Dinle normal, Yavaş yavaş hızda kelimeyi okutur
    await t.tap(find.byKey(const Key('tts_word')));
    await t.pump();
    await t.tap(find.byKey(const Key('tts_word_slow')));
    await t.pump();
    expect(calls, ['normal:$word', 'yavas:$word']);
    expect(find.byKey(const Key('tts_sentence')), findsNothing, reason: 'cümle düğmesi arka yüzde');

    // 2) Ses paketi yoksa nasıl kurulacağı söylenir
    engineOk = false;
    await t.tap(find.byKey(const Key('tts_word')));
    await t.pumpAndSettle();
    expect(find.byKey(const Key('tts_unavailable')), findsOneWidget);
    expect(find.textContaining('Metin okuma çıkışı'), findsOneWidget);
    engineOk = true;
    ScaffoldMessenger.of(t.element(find.byType(Scaffold).first)).hideCurrentSnackBar();
    await t.pumpAndSettle();

    // 3) Arka yüz: örnek cümle okunur
    calls.clear();
    await t.tap(find.text('Çevirmek için dokun'));
    await t.pumpAndSettle();
    await t.tap(find.byKey(const Key('tts_sentence')));
    await t.pump();
    expect(calls, hasLength(1));
    expect(calls.single, startsWith('normal:'));
    expect(calls.single.split(' ').length, greaterThan(3), reason: 'cümle okunmalı, tek kelime değil');
  });
}
