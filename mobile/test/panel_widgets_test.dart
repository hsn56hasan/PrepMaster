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

Map<String, dynamic> sampleDaily({bool allDone = false}) => {
      'locked': false,
      'placement': {'level': 'B2', 'mastered': 'B1'},
      'streak': 3,
      'xp_today': allDone ? 70 : 25,
      'tasks_done': allDone ? 4 : 2,
      'tasks_total': 4,
      'all_done': allDone,
      'week': [
        for (var i = 0; i < 7; i++)
          {'day': '2026-11-${18 + i}', 'label': ['Çar', 'Per', 'Cum', 'Cmt', 'Paz', 'Pzt', 'Sal'][i],
           'today': i == 6, 'completed': i >= 4, 'active': i >= 3},
      ],
      'tasks': [
        {'id': 'vocab', 'icon': 'layers', 'xp': 10, 'title': '20 kelime tekrarı', 'done': 20, 'target': 20,
         'action': {'type': 'tab', 'tab': 'flashcards'}},
        {'id': 'weakest', 'icon': 'trending-up', 'xp': 15, 'title': 'B2 Sentence Completion · 10 soru',
         'done': allDone ? 10 : 2, 'target': 10, 'action': {'type': 'practice', 'category': 'Reading', 'level': 'B2'}},
        {'id': 'questions', 'icon': 'target', 'xp': 15, 'title': 'Günün soru hedefi: 15 soru', 'done': 15, 'target': 15,
         'action': {'type': 'quick'}},
        {'id': 'mistakes', 'icon': 'shield-alert', 'xp': 10, 'title': "Hata Kasası'ndan 5 soru",
         'done': allDone ? 5 : 0, 'target': 5, 'action': {'type': 'tab', 'tab': 'mistakes'}},
      ],
      'journey': {'level': 'B2', 'correct': 26, 'total': 34, 'pct': 76, 'ready_pct': 70, 'next_level': 'C1', 'ready': true},
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

  testWidgets('Günlük görevler: kilitli, açık, tamam ve kur yolculuğu', (t) async {
    var placementOpened = 0;
    final started = <String>[];
    final nextLevels = <String>[];
    Future<void> pump(Map<String, dynamic> daily) => t.pumpWidget(MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: Column(children: [
                DailyTasksCard(daily: daily, onStartPlacement: () => placementOpened++,
                    onTask: (task) => started.add('${task['id']}')),
                if (daily['journey'] != null)
                  JourneyCard(journey: (daily['journey'] as Map).cast<String, dynamic>(), onNextLevel: nextLevels.add),
              ]),
            ),
          ),
        ));

    // Kilitli: seviye tespitine yönlendirir
    await pump({'locked': true, 'tasks': []});
    expect(find.byKey(const Key('daily_locked')), findsOneWidget);
    await t.tap(find.byKey(const Key('daily_start_placement')));
    expect(placementOpened, 1);

    // Açık: seri, XP, 7 günlük takvim, tamamlanan görevde XP, diğerlerinde Başla
    await pump(sampleDaily());
    expect(find.text('3 gün'), findsOneWidget);
    expect(find.text('25 XP'), findsOneWidget);
    expect(find.text('2/4 görev tamam'), findsOneWidget);
    expect(find.text('+10 XP'), findsOneWidget);
    expect(find.byKey(const Key('task_start_vocab')), findsNothing);
    await t.tap(find.byKey(const Key('task_start_weakest')));
    await t.pumpAndSettle();
    expect(started, ['weakest']);

    // Kur yolculuğu: %76 ≥ %70 → üst kura geç
    expect(find.text('%76'), findsOneWidget);
    await t.tap(find.byKey(const Key('journey_next')));
    await t.pumpAndSettle();
    expect(nextLevels, ['C1']);

    // Hepsi tamam
    await pump(sampleDaily(allDone: true));
    expect(find.textContaining('Bugünün görevleri tamam'), findsOneWidget);
    expect(find.text('Başla'), findsNothing);
  });
}
