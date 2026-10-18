import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/models/listening_track.dart';
import 'package:prep_master/models/writing_guide.dart';
import 'package:prep_master/theme/app_theme.dart';
import 'package:prep_master/services/api_service.dart';

void main() {
  group('Listening & Writing Evaluation Tests', () {
    test('ListeningTrack fromJson parses correctly', () {
      final jsonMap = {
        'id': 'test_lis_1',
        'university_id': 'boun',
        'level': 'C1',
        'type': 'note_taking',
        'title': 'Test Audio',
        'subtitle': 'Subtitle',
        'target_university': 'Boğaziçi',
        'duration_minutes': 15,
        'lecture_duration_seconds': 90,
        'instructions_tr': 'Not alınız',
        'audio_script': 'Hello students',
        'suggested_notes_tr': ['Note 1'],
        'questions': [
          {
            'id': 'q1',
            'question': 'What was said?',
            'options': [
              {'key': 'A', 'text': 'Option A'},
              {'key': 'B', 'text': 'Option B'},
            ],
            'correct_answer': 'A',
            'explanation_tr': 'Açıklama'
          }
        ]
      };

      final track = ListeningTrack.fromJson(jsonMap);
      expect(track.id, 'test_lis_1');
      expect(track.type, 'note_taking');
      expect(track.questions.length, 1);
      expect(track.questions.first.correctAnswer, 'A');
    });

    test('Offline AI Essay Evaluation produces accurate score and CEFR', () async {
      const sampleEssay = '''
In recent years, the rapid advancement of artificial intelligence has revolutionized medical diagnostics. In my view, while autonomous diagnostic systems introduce ethical dilemmas, their capacity to enhance diagnostic accuracy outweighs potential risks. This essay will examine how computational neural networks facilitate early disease detection and mitigate clinical error margins.

Firstly, artificial intelligence algorithms analyze medical imaging data with unprecedented precision. For instance, convolutional neural networks trained on millions of dermatological scans demonstrate diagnostic accuracy comparable to experienced oncologists. Furthermore, these automated tools assist physicians in rural clinics. Consequently, patients receive timely interventions, significantly diminishing mortality rates.

On the other hand, skeptics argue that complete reliance on automated diagnostics may undermine human clinical empathy and introduce systemic bias. Nevertheless, artificial intelligence should be conceptualized as an augmentative tool rather than an outright replacement. In conclusion, integrating artificial intelligence into clinical diagnostics represents a profound transformation in modern healthcare.
''';

      final result = await ApiService().evaluateEssay(
        essay: sampleEssay,
        prompt: 'AI in healthcare',
        universityId: 'itu',
        level: 'B2',
      );

      expect(result.wordCount, greaterThan(100));
      expect(result.overallScore, greaterThanOrEqualTo(65));
      expect(result.isPassing, isTrue);
      expect(result.detectedTransitions, isNotEmpty);
      expect(result.detectedAcademicWords, isNotEmpty);
    });

    test('SpeakingTask parses from JSON and Offline AI Speaking Evaluation scores accurately', () async {
      const sampleTranscript = '''
In my view, free higher education is essential for promoting social mobility and dismantling financial barriers. Furthermore, state-funded universities foster widespread societal innovation regardless of socioeconomic background. Consequently, public investment in tertiary education yields profound long-term economic dividends.
''';

      final result = await ApiService().evaluateSpeaking(
        transcript: sampleTranscript,
        taskId: 'spk_boun_01',
        durationSeconds: 60,
      );

      expect(result.wordCount, greaterThan(30));
      expect(result.speakingRateWpm, greaterThan(30));
      expect(result.overallScore, greaterThanOrEqualTo(60));
      expect(result.strengthsTr, isNotEmpty);
      expect(result.fluencyScore, greaterThan(0));
      expect(result.lexicalScore, greaterThan(0));
    });

    test('Mock Exam generator and Report Summary return valid structured payloads', () async {
      TestWidgetsFlutterBinding.ensureInitialized();
      SharedPreferences.setMockInitialValues({});
      final mockExam = await ApiService().getMockExam('itu');
      expect(mockExam['exam_title'], isNotNull);
      expect(mockExam['duration_minutes'], greaterThan(0));
      expect(mockExam['passing_score'], greaterThanOrEqualTo(50));

      final report = await ApiService().getReportSummary();
      expect(report['student_profile'], isNotNull);
      expect(report['readiness_status'], isNotNull);
      expect(report['average_score'], isNotNull);
    });

    test('WritingGuide with Model Essay and Pitfalls parses properly', () {
      final jsonGuide = {
        'id': 'opinion-essay',
        'title': 'Opinion / Agree-Disagree Essay',
        'description': 'Akademik fikir belirtme kompozisyonu',
        'structure': [
          {
            'section': 'Introduction',
            'elements': ['Hook', 'Background', 'Thesis Statement']
          }
        ],
        'key_transitions': ['Furthermore', 'Consequently', 'In contrast'],
        'sample_topic': 'Is artificial intelligence beneficial in medicine?',
        'band_score_tip': 'Must have explicit counter-argument refutation.',
        'model_essay': 'Full exemplar essay text with advanced academic vocabulary.',
        'model_band_score': 92,
        'annotated_strengths': ['Sophisticated AWL vocabulary', 'Flawless cohesion'],
        'common_pitfalls': ['Over-generalized thesis', 'Lack of concrete evidence']
      };

      final guide = WritingGuide.fromJson(jsonGuide);
      expect(guide.id, 'opinion-essay');
      expect(guide.modelBandScore, 92);
      expect(guide.modelEssay, contains('Full exemplar'));
      expect(guide.annotatedStrengths.length, 2);
      expect(guide.commonPitfalls.length, 2);
      expect(guide.keyTransitions.length, 3);
    });

    test('AppTheme darkTheme provides appropriate dark contrast and brightness', () {
      final dark = AppTheme.darkTheme;
      expect(dark.brightness, Brightness.dark);
      expect(dark.scaffoldBackgroundColor, AppTheme.darkSurfaceBg);
      expect(dark.colorScheme.surface, AppTheme.darkCardBg);

      final light = AppTheme.lightTheme;
      expect(light.brightness, Brightness.light);
      expect(light.scaffoldBackgroundColor, AppTheme.surfaceBg);
    });

    test('User Authentication local persistence saves, loads, and clears user', () async {
      TestWidgetsFlutterBinding.ensureInitialized();
      SharedPreferences.setMockInitialValues({});

      final api = ApiService();
      final testUser = {
        'id': 42,
        'username': 'itutest',
        'full_name': 'İTÜ Test Öğrenci',
        'email': 'test@itu.edu.tr',
        'university_id': 'itu',
        'is_verified_student': 1,
      };

      await api.saveCurrentUser(testUser);
      final loaded = await api.loadSavedUser();
      expect(loaded, isNotNull);
      expect(loaded!['username'], 'itutest');
      expect(loaded['id'], 42);

      await api.clearSavedUser();
      final cleared = await api.loadSavedUser();
      expect(cleared, isNull);
    });
  });
}

