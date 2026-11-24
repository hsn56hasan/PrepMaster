// Panel parçaları: günün planı, sekmeli ilerleme kartı (Bölümler / Kurlar / Hatalar) ve uyarı satırı.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:prep_master/widgets/panel_widgets.dart';

Map<String, dynamic> sampleOverview() => {
      'level': 'B2',
      'pool': 'school',
      'sections': [
        {'category': 'Grammar', 'total': 6, 'answered': 4, 'correct': 3},
        {'category': 'Paragraph Completion', 'total': 4, 'answered': 0, 'correct': 0},
      ],
      'levels': [
        for (final l in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
          {'level': l, 'total': 34, 'answered': l == 'B2' ? 10 : 0, 'correct': l == 'B2' ? 7 : 0},
      ],
      'mistakes_by_category': {'Reading': 3, 'Grammar': 1},
      'plan': [
        {'id': 'vocab', 'title': '20 kelime tekrarı', 'done': 20, 'target': 20, 'action': {'type': 'tab', 'tab': 'flashcards'}},
        {'id': 'weakest', 'title': 'B2 Reading · 10 soru', 'done': 2, 'target': 10,
         'action': {'type': 'practice', 'category': 'Reading', 'level': 'B2'}},
      ],
    };

void main() {
  testWidgets('Sekmeli ilerleme kartı ve günün planı', (t) async {
    final practiced = <String>[];
    final levels = <String>[];
    var mistakesOpened = 0;
    final planActions = <String>[];
    final overview = sampleOverview();

    await t.pumpWidget(MaterialApp(
      home: Scaffold(
        body: ListView(children: [
          TodayPlanCard(
            plan: (overview['plan'] as List).cast<Map<String, dynamic>>(),
            onAction: (p) => planActions.add('${p['id']}'),
          ),
          ProgressTabsCard(
            overview: overview,
            poolLabel: 'İTÜ havuzu',
            onPractice: practiced.add,
            onLevel: levels.add,
            onMistakes: () => mistakesOpened++,
          ),
        ]),
      ),
    ));

    // Plan: 1/2 tamam, ilk görev işaretli
    expect(find.text('1/2 tamam'), findsOneWidget);
    expect(find.text('20/20'), findsOneWidget);
    await t.tap(find.byKey(const Key('plan_weakest')));
    expect(planActions, ['weakest']);

    // Bölümler: sayılar ve pratik düğmesi
    expect(find.text('3/6'), findsOneWidget);
    expect(find.textContaining('İTÜ havuzu · B2'), findsOneWidget);
    await t.tap(find.byKey(const Key('section_play_0')));
    expect(practiced, ['Grammar']);

    // Kurlar: seçili kur işaretli, dokununca kur değişir
    await t.tap(find.byKey(const Key('progress_tab_1')));
    await t.pump();
    expect(find.text('B2 · seçili'), findsOneWidget);
    expect(find.text('7/34'), findsOneWidget);
    await t.tap(find.byKey(const Key('level_row_C1')));
    expect(levels, ['C1']);

    // Hatalar: kategoriye göre, dokununca Hata Kasası
    await t.tap(find.byKey(const Key('progress_tab_2')));
    await t.pump();
    expect(find.text('3 hata'), findsOneWidget);
    await t.tap(find.byKey(const Key('mistake_row_0')));
    expect(mistakesOpened, 1);
  });

  testWidgets('Boş Hata Kasası ve uyarı satırı', (t) async {
    var tapped = false;
    final overview = sampleOverview()..['mistakes_by_category'] = {};
    await t.pumpWidget(MaterialApp(
      home: Scaffold(
        body: Column(children: [
          AlertRow(icon: Icons.warning_amber_rounded, text: 'Hata Kasanda 3 çözülmemiş soru var',
              actionLabel: 'Çöz', onTap: () => tapped = true),
          ProgressTabsCard(overview: overview, poolLabel: 'Genel havuz', onPractice: (_) {}, onLevel: (_) {},
              onMistakes: () {}),
        ]),
      ),
    ));
    await t.tap(find.text('Çöz'));
    expect(tapped, isTrue);
    await t.tap(find.byKey(const Key('progress_tab_2')));
    await t.pump();
    expect(find.textContaining('Hata Kasası boş'), findsOneWidget);
  });
}
