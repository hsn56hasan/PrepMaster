import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/university.dart';
import '../services/api_service.dart';
import '../services/sync_service.dart';
import '../theme/app_theme.dart';
import 'dashboard_screen.dart';
import 'exams_screen.dart';
import 'mistake_vault_screen.dart';
import 'flashcards_screen.dart';
import 'practice_screen.dart';
import 'writing_screen.dart';
import 'analytics_screen.dart';
import 'path_screen.dart';

class HomeNavigation extends StatefulWidget {
  const HomeNavigation({super.key});

  @override
  State<HomeNavigation> createState() => _HomeNavigationState();
}

class _HomeNavigationState extends State<HomeNavigation> {
  int _currentIndex = 0;
  University? _currentUniversity;
  String _currentLevel = 'B2';
  int _mistakeCount = 0;
  bool _isLoading = true;
  bool _pathVisited = false; // Konu Yolu ilk açılışta yüklenir

  @override
  void initState() {
    super.initState();
    _initApp();
  }

  Future<void> _initApp() async {
    // Açılışta web ile eşitle: bekleyen çevrimdışı değişiklikleri gönder, sunucudaki
    // güncel ilerlemeyi (kelime, Hata Kasası, seçili üniversite/seviye) çek.
    await SyncService().syncNow();
    final prefs = await SharedPreferences.getInstance();
    final savedLevel = prefs.getString('current_level') ?? 'B2';
    final savedUniId = prefs.getString('current_uni_id') ?? 'itu';

    final universities = await ApiService().getUniversities();
    University initialUni = universities.firstWhere(
      (u) => u.id == savedUniId,
      orElse: () => universities.first,
    );

    final stats = await ApiService().getStats();
    final mCount = stats['unresolved_mistakes'] ?? 0;

    if (mounted) {
      setState(() {
        _currentUniversity = initialUni;
        _currentLevel = savedLevel;
        _mistakeCount = mCount;
        _isLoading = false;
      });
    }
  }

  void _onUniversityChange(University uni) async {
    setState(() {
      _currentUniversity = uni;
    });
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('current_uni_id', uni.id);
    await ApiService().updateProfile(universityId: uni.id, level: _currentLevel);
  }

  void _onLevelChange(String level) async {
    setState(() {
      _currentLevel = level;
    });
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('current_level', level);
    if (_currentUniversity != null) {
      await ApiService().updateProfile(universityId: _currentUniversity!.id, level: level);
    }
  }

  void _onTabSwitch(int index) {
    setState(() {
      _currentIndex = index;
      if (index == 7) _pathVisited = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading || _currentUniversity == null) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    final pages = [
      DashboardScreen(
        currentUniversity: _currentUniversity!,
        currentLevel: _currentLevel,
        onUniversityChange: _onUniversityChange,
        onLevelChange: _onLevelChange,
        onTabSwitch: _onTabSwitch,
      ),
      ExamsScreen(
        currentUniversity: _currentUniversity!,
        currentLevel: _currentLevel,
      ),
      MistakeVaultScreen(
        currentUniversity: _currentUniversity!,
        currentLevel: _currentLevel,
      ),
      FlashcardsScreen(
        currentLevel: _currentLevel,
      ),
      PracticeScreen(
        currentLevel: _currentLevel,
      ),
      WritingScreen(
        currentLevel: _currentLevel,
      ),
      const AnalyticsScreen(),
      _pathVisited ? const PathScreen() : const SizedBox.shrink(), // 7: Konu Yolu
    ];

    // Alt çubuk sırası -> sayfa indeksi (Konu Yolu ikinci sırada)
    const navPages = [0, 7, 1, 2, 3, 4];
    final navIndex = navPages.indexOf(_currentIndex);

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: navIndex < 0 ? 0 : navIndex,
        onDestinationSelected: (idx) {
          setState(() {
            _currentIndex = navPages[idx];
            if (_currentIndex == 7) _pathVisited = true;
          });
        },
        backgroundColor: Colors.white,
        elevation: 2,
        indicatorColor: AppTheme.brandLightBlue,
        destinations: [
          const NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard_rounded, color: AppTheme.brandBlue),
            label: 'Özet',
          ),
          const NavigationDestination(
            icon: Icon(Icons.route_outlined),
            selectedIcon: Icon(Icons.route_rounded, color: AppTheme.brandBlue),
            label: 'Yol',
          ),
          const NavigationDestination(
            icon: Icon(Icons.description_outlined),
            selectedIcon: Icon(Icons.description_rounded, color: AppTheme.brandBlue),
            label: 'Deneme',
          ),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _mistakeCount > 0,
              label: Text('$_mistakeCount'),
              backgroundColor: AppTheme.accentRose,
              child: const Icon(Icons.shield_outlined),
            ),
            selectedIcon: Badge(
              isLabelVisible: _mistakeCount > 0,
              label: Text('$_mistakeCount'),
              backgroundColor: AppTheme.accentRose,
              child: const Icon(Icons.shield_rounded, color: AppTheme.accentRose),
            ),
            label: 'Hatalar',
          ),
          const NavigationDestination(
            icon: Icon(Icons.layers_outlined),
            selectedIcon: Icon(Icons.layers_rounded, color: AppTheme.brandBlue),
            label: 'Kelime',
          ),
          const NavigationDestination(
            icon: Icon(Icons.quiz_outlined),
            selectedIcon: Icon(Icons.quiz_rounded, color: AppTheme.brandBlue),
            label: 'Pratik',
          ),
        ],
      ),
    );
  }
}
