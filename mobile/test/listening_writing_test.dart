import 'package:flutter_test/flutter_test.dart';
import 'package:prep_master/models/listening_track.dart';
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
  });
}

