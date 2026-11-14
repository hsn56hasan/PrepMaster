import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:prep_master/screens/forgot_password_dialog.dart';

void main() {
  testWidgets('Şifremi unuttum: geçersiz e-posta sunucuya gitmeden uyarı verir', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: ForgotPasswordDialog())));

    expect(find.text('Şifremi Unuttum'), findsOneWidget);
    expect(find.byKey(const Key('forgot_email')), findsOneWidget);
    expect(find.byKey(const Key('forgot_code')), findsNothing);

    await tester.enterText(find.byKey(const Key('forgot_email')), 'gecersiz-adres');
    await tester.tap(find.byKey(const Key('forgot_submit')));
    await tester.pump();

    expect(find.text('Lütfen geçerli bir e-posta adresi girin.'), findsOneWidget);
    expect(find.byKey(const Key('forgot_code')), findsNothing);
  });

  testWidgets('Şifremi unuttum: giriş alanındaki e-posta önceden doldurulur', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: ForgotPasswordDialog(initialEmail: 'ogrenci@itu.edu.tr')),
    ));
    final field = tester.widget<TextField>(find.byKey(const Key('forgot_email')));
    expect(field.controller!.text, 'ogrenci@itu.edu.tr');
  });
}
