import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('PrepMasterApp smoke test', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({
      'current_level': 'B2',
      'current_uni_id': 'itu',
    });

    await tester.pumpWidget(const PrepMasterApp());
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
