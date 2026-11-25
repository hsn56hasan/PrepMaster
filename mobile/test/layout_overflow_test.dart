// Telefon ekranlarında taşma / üst üste binme taraması.
//
// Her ekran küçük (320x568), orta (360x640) ve büyük (412x915) telefon boyutunda, normal ve
// büyütülmüş (%130) yazı tipiyle çizilir. Flutter'ın "RenderFlex overflowed" hataları toplanır;
// tek bir taşma bile testi düşürür ve hangi dosyanın hangi satırında olduğu raporlanır.
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/models/exam_result.dart';
import 'package:prep_master/models/listening_track.dart';
import 'package:prep_master/models/question.dart';
import 'package:prep_master/models/speaking_task.dart';
import 'package:prep_master/models/university.dart';
import 'package:prep_master/screens/analytics_screen.dart';
import 'package:prep_master/screens/auth_screen.dart';
import 'package:prep_master/screens/exam_result_screen.dart';
import 'package:prep_master/screens/exam_runner_screen.dart';
import 'package:prep_master/screens/home_navigation.dart';
import 'package:prep_master/screens/listening_screen.dart';
import 'package:prep_master/screens/locked_university_sheet.dart';
import 'package:prep_master/screens/placement_test_screen.dart';
import 'package:prep_master/screens/speaking_screen.dart';
import 'package:prep_master/screens/student_document_scan_sheet.dart';
import 'package:prep_master/screens/university_picker_dialog.dart';
import 'package:prep_master/screens/writing_screen.dart';
import 'package:prep_master/services/placement_test.dart';
import 'package:prep_master/theme/app_theme.dart';
import 'package:prep_master/widgets/panel_widgets.dart';
import 'package:prep_master/screens/exams_screen.dart';

const sizes = [Size(320, 568), Size(360, 640), Size(412, 915)];
const scales = [1.0, 1.3];

final _loc = RegExp(r'(lib/screens/[a-z_]+\.dart:\d+)');
final _how = RegExp(r'overflowed by ([\d.]+) pixels on the (\w+)');

/// Ekranı verilen boyutta çizer, taşma hatalarını "dosya:satır (N px yön)" olarak döner.
Future<Set<String>> render(WidgetTester tester, Widget screen, Size size, double scale,
    {Future<void> Function()? interact}) async {
  final found = <String>{};
  final previous = FlutterError.onError;
  FlutterError.onError = (details) {
    final text = details.toString();
    if (!text.contains('overflowed')) return; // ağ/varlık uyarıları bu taramanın konusu değil
    final where = _loc.firstMatch(text)?.group(1) ?? 'bilinmeyen konum';
    final how = _how.firstMatch(text);
    if (found.add('$where (${how?.group(1)} px ${how?.group(2)})')) {
      // Tanı için tam hata metni (hangi öğe, hangi sınır, içindekiler)
      File('build/tasma_ayrinti.txt').writeAsStringSync('==== $where\n$text\n', mode: FileMode.append);
    }
  };
  tester.view.devicePixelRatio = 2.0;
  tester.view.physicalSize = size * 2.0;
  try {
    await tester.pumpWidget(MaterialApp(
      theme: AppTheme.lightTheme.copyWith(platform: TargetPlatform.android),
      builder: (context, child) => MediaQuery(
        data: MediaQuery.of(context).copyWith(textScaler: TextScaler.linear(scale)),
        child: child!,
      ),
      home: screen,
    ));
    await settle(tester);
    if (interact != null) await interact();
  } finally {
    FlutterError.onError = previous;
    await tester.pumpWidget(const SizedBox());
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  }
  return found;
}

/// Ağ (test istemcisi 400 döner) ve varlık okumaları gerçek G/Ç'dir; sahte saatle ilerlemez.
Future<void> settle(WidgetTester tester) async {
  for (var i = 0; i < 8; i++) {
    await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 150)));
    await tester.pump(const Duration(seconds: 1));
  }
}

University _uni() {
  final list = jsonDecode(File('assets/data/universities.json').readAsStringSync()) as List;
  return University.fromJson(list.firstWhere((u) => u['id'] == 'itu') as Map<String, dynamic>);
}

List<Question> _questions() {
  final list = jsonDecode(File('assets/data/questions.json').readAsStringSync()) as List;
  // Okuma parçalı ve uzun şıklı sorular da olsun
  return list.where((q) => q['level'] == 'B2').take(6).map((q) => Question.fromJson(q)).toList();
}

/// Flutter testleri varsayılan olarak her harfi kare çizen bir test yazı tipi kullanır; yazılar
/// gerçekte olduğundan ~2 kat geniş ölçülür. Telefondakine yakın sonuç için Roboto ve simgeler yüklenir.
Future<void> loadRealFonts() async {
  final root = Platform.environment['FLUTTER_ROOT'] ?? r'C:\Projelerlutter-sdklutter';
  final dir = Directory('$root/bin/cache/artifacts/material_fonts');
  Future<ByteData> read(String name) async =>
      ByteData.sublistView(await File('${dir.path}/$name').readAsBytes());
  final roboto = FontLoader('Roboto');
  for (final f in ['roboto-regular.ttf', 'roboto-medium.ttf', 'roboto-bold.ttf', 'roboto-black.ttf',
                   'roboto-italic.ttf', 'roboto-light.ttf']) {
    roboto.addFont(read(f));
  }
  await roboto.load();
  final icons = FontLoader('MaterialIcons')..addFont(read('materialicons-regular.otf'));
  await icons.load();
}

/// Seviye tespitinde kullanılan gerçek havuz (uygulamayla gelen parçasız özgün sorular).
Map<String, List<Question>> _placementPool() {
  final list = jsonDecode(File('assets/data/questions.json').readAsStringSync()) as List;
  final pool = <String, List<Question>>{for (final l in placementLevels) l: []};
  for (final q in list) {
    final passage = q['passage'] as String?;
    if ((q['id'] as String).startsWith('q-orj-') && (passage == null || passage.isEmpty)) {
      pool[q['level']]!.add(Question.fromJson(q as Map<String, dynamic>));
    }
  }
  return pool;
}

ListeningTrack _track() {
  final list = jsonDecode(File('assets/data/listening.json').readAsStringSync()) as List;
  return ListeningTrack.fromJson(list.first as Map<String, dynamic>);
}

SpeakingTask _task() {
  final list = jsonDecode(File('assets/data/speaking.json').readAsStringSync()) as List;
  return SpeakingTask.fromJson(list.first as Map<String, dynamic>);
}

List<University> _unis() {
  final list = jsonDecode(File('assets/data/universities.json').readAsStringSync()) as List;
  return list.map((u) => University.fromJson(u as Map<String, dynamic>)).toList();
}

ExamResult _result() {
  final qs = _questions();
  return ExamResult.fromJson({
    'attempt_id': 1, 'score': 66.7, 'total_questions': qs.length, 'correct_count': 4, 'wrong_count': 2,
    'duration_seconds': 754,
    'time_analytics': {'avg_time_per_question': 125, 'time_traps_count': 2},
    'details': [
      for (var i = 0; i < qs.length; i++)
        {
          'question_id': qs[i].id, 'category': qs[i].category, 'level': qs[i].level,
          'question_text': qs[i].question, 'chosen_answer': 'A', 'correct_answer': qs[i].correctAnswer,
          'is_correct': i.isEven, 'time_spent': 90 + i * 20, 'explanation_tr': qs[i].explanationTr,
          'options': [for (final o in qs[i].options) {'key': o.key, 'text': o.text}],
        },
    ],
  });
}

void main() {
  final report = <String, Set<String>>{};

  setUpAll(loadRealFonts);

  Map<String, Object> basePrefs() => {
        'auth_token': 'test',
        'auth_user_data': jsonEncode({
          'id': 1, 'username': 'deneme', 'full_name': 'Deneme Öğrencisi Uzun Adlı',
          'email': 'deneme@example.com', 'university_id': 'itu',
          'unlocked_universities': ['itu', 'general'],
        }),
        'current_uni_id': 'itu',
        'current_level': 'B2',
      };

  setUp(() => SharedPreferences.setMockInitialValues(basePrefs()));

  Future<void> scan(WidgetTester tester, String name, Widget Function() build,
      {Future<void> Function(WidgetTester)? interact}) async {
    for (final size in sizes) {
      for (final scale in scales) {
        final issues = await render(tester, build(), size, scale,
            interact: interact == null ? null : () => interact(tester));
        for (final i in issues) {
          report.putIfAbsent(i, () => {}).add('$name @${size.width.toInt()}w x$scale');
        }
      }
    }
  }

  final tabs = ['Yol', 'Deneme', 'Hatalar', 'Kelime', 'Pratik'];

  Future<void> waitForNav(WidgetTester t) async {
    for (var i = 0; i < 30 && find.byType(NavigationBar).evaluate().isEmpty; i++) {
      await settle(t);
    }
  }

  testWidgets('Ana sekmeler', (t) async {
    await scan(t, 'Özet', () => const HomeNavigation(), interact: (t) async {
      await waitForNav(t);
      expect(find.byKey(const Key('placement_offer')), findsOneWidget);
    });
    for (final tab in tabs) {
      await scan(t, tab, () => const HomeNavigation(), interact: (t) async {
        for (var i = 0; i < 30 && find.byType(NavigationBar).evaluate().isEmpty; i++) {
          await settle(t);
        }
        await t.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text(tab)));
        await settle(t);
      });
    }
    // Seviye tespiti çözülmüşse dashboard'da teklif yerine kısa özet görünür
    SharedPreferences.setMockInitialValues(
        {...basePrefs(), PlacementTestScreen.prefLevel: 'C1', PlacementTestScreen.prefMastered: 'B2'});
    await scan(t, 'Özet+SeviyeTespiti', () => const HomeNavigation(), interact: (t) async {
      await waitForNav(t);
      expect(find.byKey(const Key('placement_summary')), findsOneWidget);
      expect(find.byKey(const Key('placement_offer')), findsNothing);
    });
  });
  testWidgets('Panel parçaları ve okul denemeleri', (t) async {
    final overview = <String, dynamic>{
      'level': 'B2',
      'pool': 'school',
      'sections': [
        for (final c in ['Grammar', 'Vocabulary', 'Reading', 'Restatement', 'Cloze Test', 'Sentence Completion',
                         'Paragraph Completion', 'Dialogue'])
          {'category': c, 'total': 34, 'answered': 12, 'correct': 9},
      ],
      'levels': [
        for (final l in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']) {'level': l, 'total': 204, 'answered': 100, 'correct': 88},
      ],
      'mistakes_by_category': {'Sentence Completion': 12, 'Paragraph Completion': 3},
      'plan': [
        {'id': 'vocab', 'title': '20 kelime tekrarı', 'done': 20, 'target': 20, 'action': {'type': 'tab', 'tab': 'flashcards'}},
        {'id': 'weakest', 'title': 'B2 Sentence Completion · 10 soru', 'done': 3, 'target': 10,
         'action': {'type': 'practice', 'category': 'Sentence Completion', 'level': 'B2'}},
        {'id': 'mistakes', 'title': "Hata Kasası'ndan 5 soru", 'done': 1, 'target': 5, 'action': {'type': 'tab', 'tab': 'mistakes'}},
      ],
    };
    Widget panel() => Scaffold(
          body: SingleChildScrollView(padding: const EdgeInsets.all(20), child: Column(children: [
            KpiGrid(tiles: const [
              KpiTile(icon: Icons.local_fire_department, iconColor: Colors.amber, label: 'Seri', value: '128 gün'),
              KpiTile(icon: Icons.assignment_turned_in_outlined, iconColor: Colors.blue, label: 'Deneme', value: '1250'),
              KpiTile(icon: Icons.trending_up, iconColor: Colors.green, label: 'Ortalama', value: '%87.5'),
              KpiTile(icon: Icons.menu_book_outlined, iconColor: Colors.indigo, label: 'Öğrenilen kelime', value: '2078/2078'),
            ]),
            AlertRow(icon: Icons.warning_amber_rounded, text: 'Hata Kasanda 125 çözülmemiş soru var',
                actionLabel: 'Çöz', onTap: () {}),
            AlertRow(tone: AlertTone.info, icon: Icons.lock_outline,
                text: 'Eskişehir Teknik soruları kilitli; ilerlemen genel havuzdan hesaplanıyor',
                actionLabel: 'Kilidi aç', onTap: () {}),
            TodayPlanCard(plan: (overview['plan'] as List).cast<Map<String, dynamic>>(), onAction: (_) {}),
            ProgressTabsCard(overview: overview, poolLabel: 'Eskişehir Teknik havuzu', onPractice: (_) {},
                onLevel: (_) {}, onMistakes: () {}),
          ])),
        );
    await scan(t, 'PanelBölümler', panel);
    for (final tab in [1, 2]) {
      await scan(t, 'PanelSekme$tab', panel, interact: (t) async {
        await t.ensureVisible(find.byKey(Key('progress_tab_$tab')));
        await t.pump();
        await t.tap(find.byKey(Key('progress_tab_$tab')));
        await t.pump();
      });
    }
    await scan(t, 'OkulDenemeleri', () => ExamsScreen(currentUniversity: _uni(), currentLevel: 'B2'));
    Map<String, dynamic> daily(bool locked) => locked
        ? {'locked': true, 'tasks': []}
        : {
            'locked': false, 'placement': {'level': 'B2', 'mastered': 'B1'}, 'streak': 128, 'xp_today': 1250,
            'tasks_done': 1, 'tasks_total': 4, 'all_done': false,
            'week': [for (final l in ['Çar', 'Per', 'Cum', 'Cmt', 'Paz', 'Pzt', 'Sal'])
              {'day': '2026-11-24', 'label': l, 'today': l == 'Sal', 'completed': l == 'Pzt', 'active': true}],
            'tasks': [
              {'id': 'vocab', 'icon': 'layers', 'xp': 10, 'title': '25 kelime tekrarı', 'done': 25, 'target': 25, 'action': {}},
              {'id': 'weakest', 'icon': 'trending-up', 'xp': 15, 'title': 'C1 Paragraph Completion · 10 soru', 'done': 3, 'target': 10, 'action': {}},
              {'id': 'questions', 'icon': 'target', 'xp': 15, 'title': 'Günün soru hedefi: 20 soru', 'done': 12, 'target': 20, 'action': {}},
              {'id': 'mistakes', 'icon': 'shield-alert', 'xp': 10, 'title': "Hata Kasası'ndan 5 soru", 'done': 0, 'target': 5, 'action': {}},
            ],
            'journey': {'level': 'C1', 'correct': 180, 'total': 204, 'pct': 88, 'ready_pct': 70, 'next_level': 'C2', 'ready': true},
          };
    for (final locked in [true, false]) {
      await scan(t, locked ? 'GörevlerKilitli' : 'Görevler', () {
        final d = daily(locked);
        return Scaffold(
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(children: [
              DailyTasksCard(daily: d, onStartPlacement: () {}, onTask: (_) {}),
              if (d['journey'] != null)
                JourneyCard(journey: (d['journey'] as Map).cast<String, dynamic>(), onNextLevel: (_) {}),
            ]),
          ),
        );
      });
    }
  });
  testWidgets('Seviye tespiti', (t) async {
    final pool = _placementPool();
    final correct = {for (final qs in pool.values) for (final q in qs) q.question: q.correctAnswer};
    Widget build() => PlacementTestScreen(currentLevel: 'A1', onApplyLevel: (_) {}, pool: pool);
    Future<void> begin(WidgetTester t) async {
      await t.ensureVisible(find.byKey(const Key('placement_begin')));
      await t.pump();
      await t.tap(find.byKey(const Key('placement_begin')));
      await settle(t);
    }

    await scan(t, 'SeviyeGiriş', build);
    await scan(t, 'SeviyeSoru', build, interact: begin);
    await scan(t, 'SeviyeSonuç', build, interact: (t) async {
      await begin(t);
      // İlk iki kurda doğru, sonra yanlış: B1 önerilir, satırların hepsi dolu olur
      for (var n = 0; n < 30 && find.byKey(const Key('placement_recommended')).evaluate().isEmpty; n++) {
        final text = t.widget<Text>(find.byKey(const Key('placement_question'))).data!;
        final level = t.widget<Text>(find.byKey(const Key('placement_level_badge'))).data!;
        final right = correct[text]!;
        final key = level.endsWith('A1') || level.endsWith('A2')
            ? right
            : ['A', 'B', 'C', 'D'].firstWhere((k) => k != right);
        final option = find.byKey(Key('placement_opt_$key'));
        await t.ensureVisible(option);
        await t.pump();
        await t.tap(option);
        await t.pump();
      }
      await settle(t);
      expect(t.widget<Text>(find.byKey(const Key('placement_recommended'))).data, 'B1');
    });
  });
  testWidgets('Giriş ekranı', (t) async => scan(t, 'Giriş', () => AuthScreen(onAuthenticated: () {})));
  testWidgets('Giriş ekranı - Kayıt', (t) async => scan(t, 'Kayıt', () => AuthScreen(onAuthenticated: () {}),
      interact: (t) async {
        await t.tap(find.text('Kayıt Ol').first);
        await settle(t);
      }));
  testWidgets('Dinleme', (t) async => scan(t, 'Dinleme', () => const ListeningScreen()));
  testWidgets('Konuşma', (t) async => scan(t, 'Konuşma', () => const SpeakingScreen()));
  testWidgets('Yazma', (t) async => scan(t, 'Yazma', () => const WritingScreen()));
  testWidgets('Analiz', (t) async => scan(t, 'Analiz', () => const AnalyticsScreen()));
  testWidgets('Sınav ekranı', (t) async =>
      scan(t, 'Sınav', () => ExamRunnerScreen(questions: _questions(), university: _uni(), level: 'B2')));
  testWidgets('Dinleme sınavı', (t) async => scan(t, 'DinlemeSınavı', () => ListeningRunnerScreen(track: _track())));
  testWidgets('Konuşma sınavı', (t) async => scan(t, 'KonuşmaSınavı', () => SpeakingRunnerScreen(task: _task())));
  testWidgets('Sınav sonucu', (t) async =>
      scan(t, 'Sonuç', () => ExamResultScreen(result: _result(), university: _uni())));
  testWidgets('Üniversite seçimi', (t) async => scan(
      t,
      'ÜniversiteSeç',
      () => Scaffold(
            body: UniversityPickerDialog(universities: _unis(), selectedUniversity: _uni(), onSelect: (_) {}),
          )));
  testWidgets('Belge tarama', (t) async =>
      scan(t, 'BelgeTara', () => const Scaffold(body: StudentDocumentScanSheet())));
  testWidgets('Kilitli üniversite (ödeme açık)', (t) async => scan(
      t,
      'Ödeme',
      () => const Scaffold(
            body: LockedUniversitySheet(
              universityId: 'boun',
              universityName: 'Boğaziçi Üniversitesi',
              config: {'paytr_configured': true, 'membership_price_try': 50.0},
            ),
          )));

  tearDownAll(() {
    final lines = report.entries.map((e) => '${e.key}  <=  ${e.value.join(", ")}').toList()..sort();
    // ignore: avoid_print
    print('\n=== TAŞMA RAPORU (${lines.length}) ===\n${lines.join('\n')}');
    File('build/tasma_raporu.txt').writeAsStringSync(lines.join('\n'));
    expect(lines, isEmpty, reason: 'Taşan yerler: ${lines.join('\n')}');
  });
}
