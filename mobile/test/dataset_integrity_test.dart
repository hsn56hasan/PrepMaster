import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:prep_master/models/listening_track.dart';
import 'package:prep_master/models/question.dart';
import 'package:prep_master/models/vocabulary.dart';

void main() {
  group('Dataset Integrity Tests for 105 Questions, 110 Vocab, 8 Listening Tracks', () {
    test('Questions JSON loads and parses all 105 items with valid fields', () {
      final file = File('assets/data/questions.json');
      expect(file.existsSync(), isTrue);

      final jsonStr = file.readAsStringSync();
      final List<dynamic> jsonList = jsonDecode(jsonStr);

      expect(jsonList.length, 105);

      for (var i = 0; i < jsonList.length; i++) {
        final item = jsonList[i];
        final question = Question.fromJson(item);
        expect(question.id.isNotEmpty, isTrue, reason: 'Item $i missing id');
        expect(question.question.isNotEmpty, isTrue, reason: 'Item $i missing question');
        expect(question.options.length, greaterThanOrEqualTo(2), reason: 'Item $i options < 2');
        expect(question.correctAnswer.isNotEmpty, isTrue, reason: 'Item $i missing correct answer');
        expect(question.explanationTr.isNotEmpty, isTrue, reason: 'Item $i missing explanation');
      }
    });

    test('Vocabulary JSON loads and parses all 110 items with valid fields', () {
      final file = File('assets/data/vocabulary.json');
      expect(file.existsSync(), isTrue);

      final jsonStr = file.readAsStringSync();
      final List<dynamic> jsonList = jsonDecode(jsonStr);

      expect(jsonList.length, 110);

      for (var i = 0; i < jsonList.length; i++) {
        final item = jsonList[i];
        final word = VocabularyItem.fromJson(item);
        expect(word.id.isNotEmpty, isTrue, reason: 'Word $i missing id');
        expect(word.word.isNotEmpty, isTrue, reason: 'Word $i missing word');
        expect(word.meaningTr.isNotEmpty, isTrue, reason: 'Word $i missing Turkish meaning');
        expect(word.exampleSentence.isNotEmpty, isTrue, reason: 'Word $i missing example sentence');
      }
    });

    test('Listening JSON loads and parses all 4 tracks with questions', () {
      final file = File('assets/data/listening.json');
      expect(file.existsSync(), isTrue);

      final jsonStr = file.readAsStringSync();
      final List<dynamic> jsonList = jsonDecode(jsonStr);

      expect(jsonList.length, 4);

      for (var i = 0; i < jsonList.length; i++) {
        final item = jsonList[i];
        final track = ListeningTrack.fromJson(item);
        expect(track.id.isNotEmpty, isTrue, reason: 'Track $i missing id');
        expect(track.title.isNotEmpty, isTrue, reason: 'Track $i missing title');
        expect(track.audioScript.isNotEmpty, isTrue, reason: 'Track $i missing audio script');
        expect(track.questions.length, greaterThan(0), reason: 'Track $i has no questions');
      }
    });
  });
}
