import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:prep_master/services/essay_import_service.dart';

Uint8List bytesOf(List<int> b) => Uint8List.fromList(b);
Uint8List ascii(String s) => Uint8List.fromList(s.codeUnits);

void main() {
  group('EssayImportService.detectKind', () {
    test('PDF, JPG, PNG ve WEBP tanınır', () {
      expect(EssayImportService.detectKind(ascii('%PDF-1.7 ...')), EssayFileKind.pdf);
      expect(EssayImportService.detectKind(bytesOf([0xFF, 0xD8, 0xFF, 0xE0, 0, 0])), EssayFileKind.image);
      expect(EssayImportService.detectKind(bytesOf([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A])), EssayFileKind.image);
      expect(EssayImportService.detectKind(ascii('RIFF\u0000\u0000\u0000\u0000WEBP')), EssayFileKind.image);
    });

    test('Diğer dosyalar reddedilir (uzantı ne olursa olsun)', () {
      expect(EssayImportService.detectKind(ascii('GIF89a......')), isNull);
      expect(EssayImportService.detectKind(bytesOf([0x50, 0x4B, 0x03, 0x04])), isNull); // docx/zip
      expect(EssayImportService.detectKind(ascii('Just text')), isNull);
      expect(EssayImportService.detectKind(Uint8List(0)), isNull);
      expect(EssayImportService.detectKind(ascii('RIFF0000WAVE')), isNull);
    });
  });

  test('Metin toparlanır ve kelimeler sayılır', () {
    const raw = 'First line   \r\nSecond line\n\n\n\nThird paragraph here.';
    final t = EssayImportService.tidy(raw);
    expect(t, 'First line\nSecond line\n\nThird paragraph here.');
    expect(EssayImportService.countWords(t), 7);
  });

  test('İzin verilen uzantılar yalnızca fotoğraf ve PDF', () {
    expect(EssayImportService.allowedExtensions, ['jpg', 'jpeg', 'png', 'webp', 'pdf']);
  });
}
