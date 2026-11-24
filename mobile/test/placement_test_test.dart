// Seviye tespit sınavı: uyarlamalı motorun kuralları, uygulama içi soru havuzu ve ekran akışı.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/models/question.dart';
import 'package:prep_master/screens/placement_test_screen.dart';
import 'package:prep_master/services/placement_test.dart';

/// Her kurda 6 soru; doğru cevap hep A.
Map<String, List<Question>> fakePool() => {
      for (final lvl in placementLevels)
        lvl: [
          for (var i = 0; i < 6; i++)
            Question(
              id: 'p-$lvl-$i',
              universityId: 'general',
              level: lvl,
              category: 'Grammar',
              question: 'Soru $lvl $i: ____',
              options: [
                for (final k in ['A', 'B', 'C', 'D']) QuestionOption(key: k, text: '$k seçeneği'),
              ],
              correctAnswer: 'A',
              explanationTr: '',
            ),
        ],
    };

/// [plan] her kur için cevap dizisi: true doğru, false yanlış.
PlacementEngine run(Map<String, List<bool>> plan) {
  final e = PlacementEngine(fakePool());
  while (!e.isFinished) {
    final lvl = e.currentLevel;
    final idx = e.results[lvl]!.answered;
    e.answer(plan[lvl]![idx] ? 'A' : 'B');
  }
  return e;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('PlacementEngine', () {
    test('hepsi doğru: C2 geçilir, kur başına 3 soru sorulur', () {
      final e = run({for (final l in placementLevels) l: [true, true, true, true]});
      expect(e.masteredLevel, 'C2');
      expect(e.recommendedLevel, 'C2');
      expect(e.answeredCount, 18);
      expect(e.results.values.every((r) => r.passed == true), isTrue);
    });

    test('ilk iki soru yanlış: sınav 2 soruda biter, A1 önerilir', () {
      final e = run({'A1': [false, false, true, true]});
      expect(e.answeredCount, 2);
      expect(e.masteredLevel, isNull);
      expect(e.recommendedLevel, 'A1');
      expect(e.results['A1']!.passed, isFalse);
      expect(e.results['A2']!.passed, isNull);
    });

    test('A2 geçilir, B1 de zorlanılır: B1 önerilir', () {
      final e = run({
        'A1': [true, true, true],
        'A2': [true, false, true, true],
        'B1': [false, true, false, true],
      });
      expect(e.masteredLevel, 'A2');
      expect(e.recommendedLevel, 'B1');
      expect(e.results['A2']!.answered, 4);
      expect(e.results['B1']!.passed, isFalse);
      expect(e.results['B2']!.passed, isNull);
      expect(e.answeredCount, 3 + 4 + 3);
      expect(e.correctCount, 3 + 3 + 1);
    });

    test('boş havuzda sınav hemen biter', () {
      final e = PlacementEngine(const {});
      expect(e.isFinished, isTrue);
      expect(e.maxQuestions, 0);
      expect(e.recommendedLevel, 'A1');
    });

    test('uygulama içi havuz: her kurda en az 4 parçasız özgün soru', () async {
      final pool = await PlacementEngine.loadPool();
      for (final lvl in placementLevels) {
        final qs = pool[lvl]!;
        expect(qs.length, greaterThanOrEqualTo(PlacementEngine.perLevel), reason: lvl);
        for (final q in qs) {
          expect(q.id, startsWith('q-orj-'));
          expect(q.passage == null || q.passage!.isEmpty, isTrue, reason: q.id);
          expect(q.options.map((o) => o.key), contains(q.correctAnswer), reason: q.id);
        }
      }
    });
  });

  testWidgets('Seviye tespit ekranı: çöz, sonucu gör, kuru ayarla', (t) async {
    SharedPreferences.setMockInitialValues({});
    final applied = <String>[];
    t.view.physicalSize = const Size(720, 1480);
    t.view.devicePixelRatio = 2.0;
    addTearDown(t.view.reset);

    await t.pumpWidget(MaterialApp(
      home: PlacementTestScreen(currentLevel: 'B2', onApplyLevel: applied.add, pool: fakePool()),
    ));
    expect(find.text('Seviyeni 5 dakikada öğren'), findsOneWidget);

    await t.tap(find.byKey(const Key('placement_begin')));
    await t.pumpAndSettle();
    expect(find.byKey(const Key('placement_question')), findsOneWidget);

    Future<void> answer(String key) async {
      await t.tap(find.byKey(Key('placement_opt_$key')));
      await t.pumpAndSettle();
    }

    // A1 ve A2: üçer doğru; B1: iki yanlış
    for (var i = 0; i < 6; i++) {
      await answer('A');
    }
    expect(t.widget<Text>(find.byKey(const Key('placement_level_badge'))).data, 'Kur B1');
    await answer('C');
    await answer('D');

    expect(t.widget<Text>(find.byKey(const Key('placement_recommended'))).data, 'B1');
    expect(find.text('A2 kurunu geçtin, B1 kurunda zorlandın.'), findsOneWidget);
    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString(PlacementTestScreen.prefLevel), 'B1');
    expect(prefs.getString(PlacementTestScreen.prefMastered), 'A2');

    await t.tap(find.byKey(const Key('placement_apply')));
    await t.pump();
    expect(applied, ['B1']);
    expect(find.byKey(const Key('placement_apply')), findsNothing);
    expect(find.byKey(const Key('placement_level_set')), findsOneWidget);

    // Tekrar çözünce baştan başlar
    await t.tap(find.byKey(const Key('placement_retry')));
    await t.pumpAndSettle();
    expect(t.widget<Text>(find.byKey(const Key('placement_level_badge'))).data, 'Kur A1');
  });
}
