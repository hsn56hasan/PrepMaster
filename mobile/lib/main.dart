import 'package:flutter/material.dart';
import 'screens/home_navigation.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const PrepMasterApp());
}

class PrepMasterApp extends StatelessWidget {
  const PrepMasterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PrepMaster',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const HomeNavigation(),
    );
  }
}
