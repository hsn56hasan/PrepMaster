import 'package:flutter/material.dart';

class AppTheme {
  static const Color brandNavy = Color(0xFF064E3B);
  static const Color brandBlue = Color(0xFF059669);
  static const Color brandLightBlue = Color(0xFFE3F3EA);

  /// Adaçayı yeşili: ikincil vurgu (#6FA287).
  static const Color brandSage = Color(0xFF6FA287);

  /// Eski mavi/çivit paletlerinin yerini alan Material paletleri (shade50..shade900).
  static const MaterialColor brandSwatch = MaterialColor(
    0xFF059669,
    <int, Color>{
      50: Color(0xFFEFFAF4),
      100: Color(0xFFD9F2E5),
      200: Color(0xFFB6E3CC),
      300: Color(0xFF8FCDB0),
      400: Color(0xFF6FA287),
      500: Color(0xFF059669),
      600: Color(0xFF05875F),
      700: Color(0xFF047857),
      800: Color(0xFF065F46),
      900: Color(0xFF064E3B),
    },
  );
  static const MaterialColor sageSwatch = MaterialColor(
    0xFF6FA287,
    <int, Color>{
      50: Color(0xFFF1F6F3),
      100: Color(0xFFDDE9E2),
      200: Color(0xFFBDD4C7),
      300: Color(0xFF9CBFAD),
      400: Color(0xFF85B199),
      500: Color(0xFF6FA287),
      600: Color(0xFF5B8C72),
      700: Color(0xFF4A775F),
      800: Color(0xFF3D624E),
      900: Color(0xFF2F4C3D),
    },
  );

  static const Color accentEmerald = Color(0xFF059669);
  static const Color accentRose = Color(0xFFE11D48);
  static const Color accentAmber = Color(0xFFD97706);

  static const Color surfaceBg = Color(0xFFEEF7F2);
  static const Color cardBg = Colors.white;
  static const Color borderSubtle = Color(0xFFE2E8F0);
  static const Color textMain = Color(0xFF0F172A);
  static const Color textMuted = Color(0xFF64748B);

  // Dark Theme Palette
  static const Color darkSurfaceBg = Color(0xFF0F172A);
  static const Color darkCardBg = Color(0xFF1E293B);
  static const Color darkBorderSubtle = Color(0xFF334155);
  static const Color darkTextMain = Color(0xFFF8FAFC);
  static const Color darkTextMuted = Color(0xFF94A3B8);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: surfaceBg,
      primaryColor: brandBlue,
      colorScheme: ColorScheme.fromSeed(
        seedColor: brandBlue,
        brightness: Brightness.light,
        primary: brandBlue,
        secondary: brandNavy,
        surface: cardBg,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 1,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: textMain,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
        iconTheme: IconThemeData(color: textMain),
      ),
      cardTheme: CardThemeData(
        color: cardBg,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: borderSubtle, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: brandBlue,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
        ),
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: darkSurfaceBg,
      primaryColor: brandBlue,
      colorScheme: const ColorScheme.dark(
        primary: brandBlue,
        secondary: Color(0xFF6FA287),
        surface: darkCardBg,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: darkCardBg,
        elevation: 0,
        scrolledUnderElevation: 1,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: darkTextMain,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
        iconTheme: IconThemeData(color: darkTextMain),
      ),
      cardTheme: CardThemeData(
        color: darkCardBg,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: darkBorderSubtle, width: 1),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: darkCardBg,
        indicatorColor: const Color(0xFF064E3B),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const IconThemeData(color: Colors.white);
          }
          return const IconThemeData(color: darkTextMuted);
        }),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: brandBlue,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
        ),
      ),
    );
  }
}
