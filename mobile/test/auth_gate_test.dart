import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/main.dart';
import 'package:prep_master/screens/auth_screen.dart';
import 'package:prep_master/screens/home_navigation.dart';

void main() {
  testWidgets('Oturum yoksa uygulama giriş ekranıyla açılır, içerik görünmez', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepMasterApp());
    await tester.pumpAndSettle();
    expect(find.byType(AuthScreen), findsOneWidget);
    expect(find.byType(HomeNavigation), findsNothing);
    expect(find.byKey(const Key('auth_login_submit')), findsOneWidget);
  });

  testWidgets('Sunucu reddederse eski yerel kullanıcı kopyasıyla içeri girilmez', (tester) async {
    // Token var ama sunucu doğrulamıyor ve kayıtlı kullanıcı yok -> giriş ekranı
    SharedPreferences.setMockInitialValues({'auth_token': 'gecersiz'});
    await tester.pumpWidget(const PrepMasterApp());
    await tester.pumpAndSettle();
    expect(find.byType(AuthScreen), findsOneWidget);
  });

  testWidgets('Boş bilgilerle giriş denenince hata gösterilir', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepMasterApp());
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('auth_login_submit')));
    await tester.pump();
    expect(find.byKey(const Key('auth_error')), findsOneWidget);
  });

  testWidgets('Kayıtta sözleşme onayı olmadan hesap açılmaz', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const PrepMasterApp());
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
}
