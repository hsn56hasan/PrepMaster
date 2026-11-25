import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/main.dart';
import 'package:prep_master/screens/auth_screen.dart';
import 'package:prep_master/screens/home_navigation.dart';

void main() {
  testWidgets('Oturum yoksa uygulama giriş ekranıyla açılır, içerik görünmez', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepKampusApp());
    await tester.pumpAndSettle();
    expect(find.byType(AuthScreen), findsOneWidget);
    expect(find.byType(HomeNavigation), findsNothing);
    expect(find.byKey(const Key('auth_login_submit')), findsOneWidget);
  });

  testWidgets('Sunucu reddederse eski yerel kullanıcı kopyasıyla içeri girilmez', (tester) async {
    // Token var ama sunucu doğrulamıyor ve kayıtlı kullanıcı yok -> giriş ekranı
    SharedPreferences.setMockInitialValues({'auth_token': 'gecersiz'});
    await tester.pumpWidget(const PrepKampusApp());
    await tester.pumpAndSettle();
    expect(find.byType(AuthScreen), findsOneWidget);
  });

  testWidgets('Boş bilgilerle giriş denenince hata gösterilir', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepKampusApp());
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('auth_login_submit')));
    await tester.pump();
    expect(find.byKey(const Key('auth_error')), findsOneWidget);
  });

  testWidgets('Kayıtta sözleşme onayı olmadan hesap açılmaz', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepKampusApp());
    await tester.pumpAndSettle();
    await tester.tap(find.text('Kayıt Ol').first);
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('auth_reg_name')), 'Deneme Öğrenci');
    await tester.enterText(find.byKey(const Key('auth_reg_user')), 'deneme');
    await tester.enterText(find.byKey(const Key('auth_reg_email')), 'deneme@example.com');
    await tester.enterText(find.byKey(const Key('auth_reg_pass')), 'Parola123!');
    await tester.dragUntilVisible(
        find.byKey(const Key('auth_reg_submit')), find.byType(ListView).last, const Offset(0, -200));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('auth_reg_submit')));
    await tester.pump();
    expect(find.textContaining('Kullanıcı Sözleşmesi'), findsWidgets);
    expect(find.byKey(const Key('auth_error')), findsOneWidget);
    expect(find.byType(HomeNavigation), findsNothing);
  });

  testWidgets('Kayıt onayları ayrı ve boş başlar; aydınlatma okundu bilgisi de zorunludur', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepKampusApp());
    await tester.pumpAndSettle();
    await tester.tap(find.text('Kayıt Ol').first);
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('auth_reg_name')), 'Deneme Öğrenci');
    await tester.enterText(find.byKey(const Key('auth_reg_user')), 'deneme');
    await tester.enterText(find.byKey(const Key('auth_reg_email')), 'deneme@example.com');
    await tester.enterText(find.byKey(const Key('auth_reg_pass')), 'Parola123!');
    await tester.dragUntilVisible(
        find.byKey(const Key('reg_terms')), find.byType(ListView).last, const Offset(0, -200));
    await tester.pumpAndSettle();
    await tester.dragUntilVisible(
        find.byKey(const Key('reg_marketing')), find.byType(ListView).last, const Offset(0, -120));
    await tester.pumpAndSettle();
    for (final k in ['reg_terms', 'reg_privacy', 'reg_marketing']) {
      expect(find.byKey(Key(k)), findsOneWidget, reason: k);
      expect(tester.widget<Checkbox>(find.byKey(Key(k))).value, isFalse, reason: k);
    }
    expect(find.byKey(const Key('reg_explicit')), findsNothing); // açık rıza kutusu kaldırıldı
    await tester.ensureVisible(find.byKey(const Key('reg_terms')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('reg_terms')));
    await tester.pump();
    await tester.dragUntilVisible(
        find.byKey(const Key('auth_reg_submit')), find.byType(ListView).last, const Offset(0, -200));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('auth_reg_submit')));
    await tester.pump();
    final error = tester.widget<Text>(find.byKey(const Key('auth_error')));
    expect(error.data, contains('Aydınlatma'));
    expect(error.data, isNot(contains('Sözleşmesi')));
    expect(find.byType(HomeNavigation), findsNothing);
  });
}
