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
import 'package:prep_master/screens/speaking_screen.dart';
import 'package:prep_master/screens/student_document_scan_sheet.dart';
import 'package:prep_master/screens/university_picker_dialog.dart';
import 'package:prep_master/screens/writing_screen.dart';
import 'package:prep_master/theme/app_theme.dart';

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

  setUp(() {
    SharedPreferences.setMockInitialValues({
      'auth_token': 'test',
      'auth_user_data': jsonEncode({
        'id': 1, 'username': 'deneme', 'full_name': 'Deneme Öğrencisi Uzun Adlı',
        'email': 'deneme@example.com', 'university_id': 'itu',
        'unlocked_universities': ['itu', 'general'],
      }),
      'current_uni_id': 'itu',
      'current_level': 'B2',
    });
  });

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

  final tabs = ['Deneme', 'Hatalar', 'Kelime', 'Pratik'];

  testWidgets('Ana sekmeler', (t) async {
    await scan(t, 'Özet', () => const HomeNavigation());
    for (final tab in tabs) {
      await scan(t, tab, () => const HomeNavigation(), interact: (t) async {
        for (var i = 0; i < 30 && find.byType(NavigationBar).evaluate().isEmpty; i++) {
          await settle(t);
        }
        await t.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text(tab)));
        await settle(t);
      });
    }
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
