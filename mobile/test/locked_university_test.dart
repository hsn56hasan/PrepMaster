import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/screens/locked_university_sheet.dart';
import 'package:prep_master/screens/university_paywall_sheet.dart';

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('Kilitli paket ekranı: fiyat, kart alanı ya da dış bağlantı yok', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: LockedUniversitySheet(universityId: 'boun', universityName: 'Boğaziçi Üniversitesi'),
      ),
    ));

    expect(find.text('Boğaziçi Üniversitesi'), findsOneWidget);
    expect(find.byKey(const Key('btn_locked_refresh')), findsOneWidget);
    expect(find.byKey(const Key('btn_locked_student_scan')), findsOneWidget);
    // Google Play: uygulama içinde başka ödeme yoluna yönlendirme yok
    expect(find.textContaining('TL'), findsNothing);
    expect(find.textContaining('http'), findsNothing);
    expect(find.byKey(const Key('input_card_number')), findsNothing);
  });

  testWidgets('Yenile: oturum ve bağlantı yokken paket açılmaz, durum bildirilir', (tester) async {
    bool unlocked = false;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: LockedUniversitySheet(
          universityId: 'boun',
          universityName: 'Boğaziçi Üniversitesi',
          onUnlockSuccess: () => unlocked = true,
        ),
      ),
    ));
    await tester.tap(find.byKey(const Key('btn_locked_refresh')));
    await tester.pumpAndSettle();
    expect(unlocked, isFalse);
    expect(find.byKey(const Key('locked_status')), findsOneWidget);
  });

  testWidgets('Sunucu demo modunda değilse simüle kart formu açılmaz', (tester) async {
    late BuildContext ctx;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(body: Builder(builder: (c) {
        ctx = c;
        return const SizedBox();
      })),
    ));
    UniversityPaywallSheet.show(ctx, universityId: 'boun', universityName: 'Boğaziçi Üniversitesi');
    await tester.pumpAndSettle();
    expect(find.byType(LockedUniversitySheet), findsOneWidget);
    expect(find.byKey(const Key('input_card_number')), findsNothing);
  });
}
