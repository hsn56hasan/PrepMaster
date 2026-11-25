// Konu Yolu: alıştırma motoru, ders ekranı (baştan sona doğru çözüm, kalp bitişi), harita ekranı
// ve küçük/büyük telefonda büyütülmüş yazıyla taşma taraması.
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:prep_master/models/lesson_path.dart';
import 'package:prep_master/screens/lesson_screen.dart';
import 'package:prep_master/screens/path_screen.dart';
import 'package:prep_master/services/lesson_engine.dart';
import 'package:prep_master/services/speech_service.dart';
import 'package:prep_master/theme/app_theme.dart';

final Map<String, dynamic> _lessons =
    jsonDecode(File('../data/lessons.json').readAsStringSync()) as Map<String, dynamic>;

Map<String, dynamic> _topic(String id) {
  for (final lv in _lessons['levels'] as List) {
    for (final u in lv['units'] as List) {
      for (final t in u['topics'] as List) {
        if (t['id'] == id) return Map<String, dynamic>.from(t as Map);
      }
    }
  }
  throw StateError(id);
}

Map<String, dynamic> _topicBundle(String id, String level) =>
    {'kind': 'topic', 'id': id, 'level': level, 'title_tr': _topic(id)['title_tr'], 'unit_title': 'Ünite', 'topics': [_topic(id)]};

Map<String, dynamic> _unitBundle(String level, int unit) {
  final lv = (_lessons['levels'] as List).firstWhere((l) => l['level'] == level);
  final u = (lv['units'] as List)[unit];
  return {'kind': 'unit', 'id': u['id'], 'level': level, 'title_tr': 'Ünite tekrarı', 'topics': u['topics']};
}

Map<String, dynamic> _overview({String current = 'b1-03'}) {
  final lv = (_lessons['levels'] as List).firstWhere((l) => l['level'] == 'B1');
  var reached = false;
  final units = <Map<String, dynamic>>[];
  for (var i = 0; i < 4; i++) {
    final u = (lv['units'] as List)[i];
    final topics = <Map<String, dynamic>>[];
    for (final t in u['topics'] as List) {
      final isCur = t['id'] == current;
      if (isCur) reached = true;
      topics.add({
        'id': t['id'], 'title_tr': t['title_tr'], 'title_en': t['title_en'], 'icon': t['icon'],
        'status': isCur ? 'current' : (reached ? 'locked' : 'done'),
        'stars': reached ? 0 : 3, 'best_pct': reached ? 0 : 100,
      });
    }
    units.add({
      'id': u['id'], 'index': i + 1, 'title_tr': u['title_tr'],
      'done': topics.where((t) => t['status'] == 'done').length, 'total': topics.length,
      'review_unlocked': i == 0 && !reached, 'review_stars': 0, 'topics': topics,
    });
  }
  return {
    'start_level': 'B1', 'selected_level': 'B1', 'current_topic': current,
    'levels': [
      for (final l in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        {'level': l, 'title': 'Seviye', 'unlocked': ['A1', 'A2', 'B1'].contains(l), 'done': l == 'B1' ? 2 : 20, 'total': 20},
    ],
    'units': units,
    'stats': {'xp_total': 1250, 'completed': 42, 'total': 120, 'perfect': 30, 'review_available': true},
  };
}

Future<void> loadRealFonts() async {
  final root = Platform.environment['FLUTTER_ROOT'] ?? r'C:\Projeler\flutter-sdk\flutter';
  final dir = Directory('$root/bin/cache/artifacts/material_fonts');
  Future<ByteData> read(String name) async => ByteData.sublistView(await File('${dir.path}/$name').readAsBytes());
  final roboto = FontLoader('Roboto');
  for (final f in ['roboto-regular.ttf', 'roboto-medium.ttf', 'roboto-bold.ttf', 'roboto-black.ttf']) {
    roboto.addFont(read(f));
  }
  await roboto.load();
  final icons = FontLoader('MaterialIcons')..addFont(read('materialicons-regular.otf'));
  await icons.load();
}

Future<void> pumpApp(WidgetTester t, Widget home, {Size size = const Size(412, 915), double scale = 1.0}) async {
  t.view.devicePixelRatio = 2.0;
  t.view.physicalSize = size * 2.0;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  await t.pumpWidget(MaterialApp(
    theme: AppTheme.lightTheme,
    builder: (context, child) => MediaQuery(
      data: MediaQuery.of(context).copyWith(textScaler: TextScaler.linear(scale)),
      child: child!,
    ),
    home: home,
  ));
  await settle(t);
}

/// Haritadaki "BAŞLA" düğümü sürekli nabız attığı için pumpAndSettle yerine sabit adımlarla ilerlenir.
Future<void> settle(WidgetTester t) async {
  for (var i = 0; i < 12; i++) {
    await t.pump(const Duration(milliseconds: 100));
  }
}

String _optionText(WidgetTester t, int i) {
  final texts = find.descendant(of: find.byKey(Key('lesson_option_$i')), matching: find.byType(Text));
  return (t.widget<Text>(texts.last)).data ?? '';
}

/// Ekrandaki alıştırmayı doğru cevaplar (alıştırma listesi aynı tohumla üretilmiş kopyadan bilinir).
Future<void> answerCorrectly(WidgetTester t, Exercise ex) async {
  switch (ex.type) {
    case ExerciseType.choice:
    case ExerciseType.listen:
    case ExerciseType.quiz:
      for (var i = 0; i < ex.options.length; i++) {
        if (_optionText(t, i) == ex.answer) {
          await t.ensureVisible(find.byKey(Key('lesson_option_$i')));
          await t.tap(find.byKey(Key('lesson_option_$i')));
          break;
        }
      }
      await t.pump();
      await t.tap(find.byKey(const Key('lesson_check')));
      break;
    case ExerciseType.match:
      for (final p in ex.pairs) {
        await t.ensureVisible(find.byKey(Key('lesson_match_en_${p.key}')));
        await t.tap(find.byKey(Key('lesson_match_en_${p.key}')));
        await t.pump();
        await t.ensureVisible(find.byKey(Key('lesson_match_tr_${p.value}')));
        await t.tap(find.byKey(Key('lesson_match_tr_${p.value}')));
        await t.pump();
      }
      break;
    case ExerciseType.order:
      final used = <int>{};
      for (final w in ex.answer.split(' ')) {
        final i = List.generate(ex.tokens.length, (k) => k).firstWhere((k) => !used.contains(k) && ex.tokens[k] == w);
        used.add(i);
        await t.ensureVisible(find.byKey(Key('lesson_token_$i')));
        await t.tap(find.byKey(Key('lesson_token_$i')));
        await t.pump();
      }
      await t.tap(find.byKey(const Key('lesson_check')));
      break;
    case ExerciseType.type:
      await t.enterText(find.byKey(const Key('lesson_type_input')), ex.answer);
      await t.pump();
      await t.tap(find.byKey(const Key('lesson_check')));
      break;
  }
  await t.pumpAndSettle();
}

void main() {
  setUpAll(loadRealFonts);
  setUp(() => SpeechService.debugOverride = (text, {required bool slow}) async => true);
  tearDown(() => SpeechService.debugOverride = null);

  group('LessonEngine', () {
    test('tek konudan 13, üniteden 15 alıştırma; bütün türler var', () {
      final one = LessonEngine.build(_topicBundle('a1-01', 'A1'), random: Random(3));
      expect(one.length, 13);
      expect(one.map((e) => e.type).toSet(), ExerciseType.values.toSet());
      final unit = LessonEngine.build(_unitBundle('B2', 1), random: Random(3));
      expect(unit.length, 15);
      for (final e in [...one, ...unit]) {
        if (e.options.isNotEmpty) {
          expect(e.options, contains(e.answer));
          expect(e.options.toSet().length, e.options.length);
        }
      }
    });

    test('her seviyenin her konusundan alıştırma üretilir', () {
      for (final lv in _lessons['levels'] as List) {
        for (final u in lv['units'] as List) {
          for (final t in u['topics'] as List) {
            final ex = LessonEngine.build(_topicBundle(t['id'] as String, lv['level'] as String), random: Random(1));
            expect(ex.length, 13, reason: '${t['id']}');
          }
        }
      }
    });

    test('B1 ve üstünde cümle kurmada fazladan kelime var, A seviyesinde yok', () {
      final a = LessonEngine.build(_topicBundle('a2-05', 'A2'), random: Random(2)).where((e) => e.type == ExerciseType.order);
      final b = LessonEngine.build(_topicBundle('b2-05', 'B2'), random: Random(2)).where((e) => e.type == ExerciseType.order);
      for (final e in a) {
        expect(e.tokens.length, e.answer.split(' ').length);
      }
      for (final e in b) {
        expect(e.tokens.length, greaterThan(e.answer.split(' ').length));
      }
    });

    test('yazma kontrolü: büyük harf, noktalama, artikel ve tek harf hatası', () {
      expect(LessonEngine.checkTyped('Good Morning!', 'good morning').ok, isTrue);
      expect(LessonEngine.checkTyped('the weather', 'weather'), (ok: true, typo: false));
      expect(LessonEngine.checkTyped('wether', 'weather'), (ok: true, typo: true));
      expect(LessonEngine.checkTyped('cat', 'car').ok, isFalse); // kısa kelimede yazım toleransı yok
      expect(LessonEngine.checkTyped('', 'hello').ok, isFalse);
      expect(LessonEngine.starsFor(100), 3);
      expect(LessonEngine.starsFor(85), 2);
      expect(LessonEngine.starsFor(49), 0);
    });
  });

  testWidgets('ders baştan sona doğru çözülünce kusursuz sonuç gönderilir', (t) async {
    final bundle = _topicBundle('a1-03', 'A1');
    final expected = LessonEngine.build(bundle, random: Random(7));
    Map<String, int>? sent;
    await pumpApp(
      t,
      LessonScreen(
        kind: 'topic',
        id: 'a1-03',
        random: Random(7),
        loader: (kind, id) async => PathResponse(200, bundle, null),
        sender: ({required nodeId, required correct, required total}) async {
          sent = {'correct': correct, 'total': total};
          expect(nodeId, 'a1-03');
          return const PathResponse(200, {'stars': 3, 'best_stars': 3, 'pct': 100, 'xp_gained': 15,
              'first_completion': true, 'next_topic': 'a1-04'}, null);
        },
      ),
    );
    expect(find.text('BU DERSİN KELİMELERİ'), findsOneWidget);
    await t.tap(find.byKey(const Key('lesson_start')));
    await t.pumpAndSettle();

    for (final ex in expected) {
      expect(find.text(ex.prompt), findsOneWidget);
      await answerCorrectly(t, ex);
      expect(find.byKey(const Key('lesson_continue')), findsOneWidget, reason: ex.type.name);
      expect(find.text('Doğru cevap:'), findsNothing, reason: ex.type.name);
      await t.tap(find.byKey(const Key('lesson_continue')));
      await t.pumpAndSettle();
    }
    expect(sent, {'correct': 13, 'total': 13});
    expect(find.text('Kusursuz!'), findsOneWidget);
    expect(find.text('+15'), findsOneWidget);
    expect(find.byKey(const Key('lesson_next')), findsOneWidget);
  });

  testWidgets('5 yanlışta kalpler biter, sonuç gönderilmez, ders yeniden başlar', (t) async {
    var sent = false;
    await pumpApp(
      t,
      LessonScreen(
        kind: 'topic',
        id: 'b1-01',
        random: Random(4),
        loader: (kind, id) async => PathResponse(200, _topicBundle('b1-01', 'B1'), null),
        sender: ({required nodeId, required correct, required total}) async {
          sent = true;
          return const PathResponse(200, {}, null);
        },
      ),
    );
    await t.tap(find.byKey(const Key('lesson_start')));
    await t.pumpAndSettle();
    for (var i = 0; i < kLessonHearts; i++) {
      await t.tap(find.byKey(const Key('lesson_skip')));
      await t.pumpAndSettle();
      expect(find.text('Doğru cevap:'), findsOneWidget);
      await t.tap(find.byKey(const Key('lesson_continue')));
      await t.pumpAndSettle();
    }
    expect(find.text('Kalplerin bitti'), findsOneWidget);
    expect(sent, isFalse);
    await t.tap(find.byKey(const Key('lesson_retry')));
    await t.pumpAndSettle();
    expect(find.byKey(const Key('lesson_start')), findsOneWidget);
  });

  testWidgets('kilitli ders sunucu hatasını gösterir', (t) async {
    await pumpApp(
      t,
      LessonScreen(
        kind: 'topic',
        id: 'c2-01',
        loader: (kind, id) async => const PathResponse(403, null, 'Bu konu henüz kilitli. Önceki dersi tamamla.'),
      ),
    );
    expect(find.text('Bu konu henüz kilitli. Önceki dersi tamamla.'), findsOneWidget);
  });

  testWidgets('harita: düğümler, BAŞLA balonu, kilitli düğüm uyarısı ve seviye değişimi', (t) async {
    final asked = <String?>[];
    await pumpApp(
      t,
      PathScreen(loader: ({level}) async {
        asked.add(level);
        return PathResponse(200, _overview(), null);
      }),
    );
    expect(find.text('Konu Yolu'), findsOneWidget);
    expect(find.text('1250'), findsOneWidget);
    expect(find.text('BAŞLA'), findsOneWidget);
    expect(find.byKey(const Key('path_node_b1-01')), findsOneWidget);
    await t.scrollUntilVisible(find.byKey(const Key('path_node_b1-04')), 200,
        scrollable: find.descendant(of: find.byKey(const Key('path_list')), matching: find.byType(Scrollable)));
    await t.ensureVisible(find.byKey(const Key('path_node_b1-04')));
    await settle(t);
    await t.tap(find.byKey(const Key('path_node_b1-04')));
    await t.pump();
    expect(find.text('Bu ders kilitli. Önce sıradaki dersi bitir.'), findsOneWidget);
    await t.drag(find.byKey(const Key('path_list')), const Offset(0, 3000));
    await settle(t);
    await t.tap(find.byKey(const Key('path_level_A2')));
    await settle(t);
    expect(asked.last, 'A2');
  });

  testWidgets('küçük ve büyük telefonda, büyük yazıyla taşma yok', (t) async {
    final found = <String>[];
    final previous = FlutterError.onError;
    FlutterError.onError = (d) {
      if (d.toString().contains('overflowed')) found.add(d.toString().split('\n').take(6).join(' | '));
    };
    try {
      for (final size in const [Size(320, 568), Size(412, 915)]) {
        for (final scale in const [1.0, 1.3]) {
          await pumpApp(t, PathScreen(loader: ({level}) async => PathResponse(200, _overview(), null)),
              size: size, scale: scale);
          // Ders: tanıtım ve her alıştırma türü (yanlış geri bildirimi dahil)
          await pumpApp(
            t,
            LessonScreen(
              kind: 'topic',
              id: 'c1-13',
              random: Random(9),
              loader: (k, i) async => PathResponse(200, _topicBundle('c1-13', 'C1'), null),
              sender: ({required nodeId, required correct, required total}) async =>
                  const PathResponse(200, {'stars': 0, 'xp_gained': 0}, null),
            ),
            size: size,
            scale: scale,
          );
          await t.tap(find.byKey(const Key('lesson_start')));
          await t.pumpAndSettle();
          for (var i = 0; i < 4; i++) {
            await t.tap(find.byKey(const Key('lesson_skip')));
            await t.pumpAndSettle();
            await t.tap(find.byKey(const Key('lesson_continue')));
            await t.pumpAndSettle();
          }
          await pumpApp(
            t,
            LessonScreen(
              kind: 'unit',
              id: 'b2-u2',
              loader: (k, i) async => PathResponse(200, _unitBundle('B2', 1), null),
            ),
            size: size,
            scale: scale,
          );
        }
      }
    } finally {
      FlutterError.onError = previous;
    }
    expect(found, isEmpty);
  });
}

