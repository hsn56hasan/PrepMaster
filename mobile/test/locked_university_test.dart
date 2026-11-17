import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/screens/locked_university_sheet.dart';
import 'package:prep_master/screens/university_paywall_sheet.dart';

Widget _sheet({Map<String, dynamic>? config, VoidCallback? onUnlock}) => MaterialApp(
      home: Scaffold(
        body: LockedUniversitySheet(
          universityId: 'boun',
          universityName: 'Boğaziçi Üniversitesi',
          onUnlockSuccess: onUnlock,
          config: config,
        ),
      ),
    );

const _paytrOn = {'paytr_configured': true, 'membership_price_try': 50.0};
const _paytrOff = {'paytr_configured': false, 'membership_price_try': 50.0};

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('Ödeme kapalıyken fiyat/ödeme düğmesi yok; belge ve Yenile var', (tester) async {
    await tester.pumpWidget(_sheet(config: _paytrOff));
    await tester.pumpAndSettle();
    expect(find.text('Boğaziçi Üniversitesi'), findsOneWidget);
    expect(find.byKey(const Key('locked_payment_unavailable')), findsOneWidget);
    expect(find.byKey(const Key('btn_locked_pay')), findsNothing);
    expect(find.byKey(const Key('btn_locked_refresh')), findsOneWidget);
    expect(find.byKey(const Key('btn_locked_student_scan')), findsOneWidget);
  });

  testWidgets('Ödeme açıkken fiyat görünür; kart bilgisi uygulamada istenmez', (tester) async {
    await tester.pumpWidget(_sheet(config: _paytrOn));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('locked_price')), findsOneWidget);
    expect(find.text('50 TL'), findsOneWidget);
    expect(find.byKey(const Key('btn_locked_pay')), findsOneWidget);
    expect(find.byKey(const Key('locked_phone')), findsOneWidget);
    // Kart PayTR'nin sayfasında girilir
    expect(find.byKey(const Key('input_card_number')), findsNothing);
  });

  testWidgets('Telefon ve ön bilgilendirme onayı olmadan ödeme başlamaz', (tester) async {
    bool unlocked = false;
    await tester.pumpWidget(_sheet(config: _paytrOn, onUnlock: () => unlocked = true));
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.byKey(const Key('btn_locked_pay')));
    await tester.tap(find.byKey(const Key('btn_locked_pay')));
    await tester.pump();
    expect(find.textContaining('cep telefonu'), findsOneWidget);

    await tester.enterText(find.byKey(const Key('locked_phone')), '0532 123 45 67');
    await tester.ensureVisible(find.byKey(const Key('btn_locked_pay')));
    await tester.tap(find.byKey(const Key('btn_locked_pay')));
    await tester.pump();
    expect(find.textContaining('Ön Bilgilendirme Formu ve Mesafeli'), findsWidgets);
    expect(find.byKey(const Key('locked_status')), findsOneWidget);
    expect(unlocked, isFalse);
  });

  testWidgets('Sunucuya ulaşılamazsa ödeme sayfası açılmaz, paket açılmaz', (tester) async {
    bool unlocked = false;
    await tester.pumpWidget(_sheet(config: _paytrOn, onUnlock: () => unlocked = true));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('locked_phone')), '05321234567');
    await tester.ensureVisible(find.byKey(const Key('locked_pre_info')));
    await tester.tap(find.byKey(const Key('locked_pre_info')));
    await tester.ensureVisible(find.byKey(const Key('btn_locked_pay')));
    await tester.tap(find.byKey(const Key('btn_locked_pay')));
    await tester.pumpAndSettle();
    expect(unlocked, isFalse);
    expect(find.byKey(const Key('locked_status')), findsOneWidget);
  });

  testWidgets('Yenile: oturum ve bağlantı yokken paket açılmaz, durum bildirilir', (tester) async {
    bool unlocked = false;
    await tester.pumpWidget(_sheet(config: _paytrOff, onUnlock: () => unlocked = true));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('btn_locked_refresh')));
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
