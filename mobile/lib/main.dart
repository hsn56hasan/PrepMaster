import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/auth_screen.dart';
import 'screens/home_navigation.dart';
import 'services/api_service.dart';
import 'services/auth_http.dart';
import 'theme/app_theme.dart';

// Global ValueNotifier for reactive theme switching
final ValueNotifier<ThemeMode> themeModeNotifier = ValueNotifier(ThemeMode.light);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    final prefs = await SharedPreferences.getInstance();
    final savedTheme = prefs.getString('theme_mode');
    if (savedTheme == 'dark') {
      themeModeNotifier.value = ThemeMode.dark;
    }
  } catch (_) {}
  runApp(const PrepKampusApp());
}

class PrepKampusApp extends StatelessWidget {
  const PrepKampusApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeModeNotifier,
      builder: (context, currentMode, _) {
        return MaterialApp(
          title: 'PrepKampüs',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: currentMode,
          home: const AuthGate(),
        );
      },
    );
  }
}

/// Uygulamanın kapısı: geçerli oturum yoksa giriş ekranı, varsa uygulama.
/// Sunucu oturumu reddederse (401) yerel kopyaya güvenilmez, yeniden giriş istenir.
/// Bağlantı yoksa önceki oturumla açılır (yalnız ücretsiz içerik çevrimdışı çalışır).
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  /// Çıkış yapınca bütün sayfaları kapatıp giriş ekranına döner.
  static Future<void> signOut(BuildContext context) async {
    await ApiService().clearSavedUser();
    if (!context.mounted) return;
    Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const AuthGate()),
      (_) => false,
    );
  }

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _checking = true;
  bool _signedIn = false;

  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    bool ok = false;
    final token = await AuthHttp.readToken();
    if (token != null && token.isNotEmpty) {
      ok = await ApiService().getCurrentUser() != null;
    }
    if (!mounted) return;
    setState(() {
      _signedIn = ok;
      _checking = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (!_signedIn) {
      return AuthScreen(onAuthenticated: () => setState(() => _signedIn = true));
    }
    return const HomeNavigation();
  }
}
