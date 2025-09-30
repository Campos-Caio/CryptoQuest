import 'package:flutter/material.dart';

/// Sistema de cores centralizado para o CryptoQuest
/// Garante consistência visual em todo o aplicativo
class AppColors {
  // Cores principais
  static const Color primary = Color(0xFF6926C4);
  static const Color secondary = Color(0xFF7F5AF0);
  static const Color accent = Color(0xFF00FFC8);

  // Cores de fundo
  static const Color background = Color(0xFF16161A);
  static const Color surface = Color(0xFF242629);
  static const Color surfaceVariant = Color(0xFF2A2D3A);

  // Cores de texto
  static const Color onPrimary = Colors.white;
  static const Color onSecondary = Colors.white;
  static const Color onBackground = Colors.white;
  static const Color onSurface = Colors.white;
  static const Color onSurfaceVariant = Color(0xFF94A1B2);

  // Cores de estado
  static const Color success = Color(0xFF38A169);
  static const Color warning = Color(0xFFD69E2E);
  static const Color error = Color(0xFFE53E3E);
  static const Color info = Color(0xFF3182CE);

  // Cores neutras
  static const Color white = Colors.white;
  static const Color black = Colors.black;
  static const Color transparent = Colors.transparent;

  // Gradientes
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient accentGradient = LinearGradient(
    colors: [accent, Color(0xFF00D4AA)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient successGradient = LinearGradient(
    colors: [success, Color(0xFF48BB78)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Cores com opacidade
  static Color primaryWithOpacity(double opacity) =>
      primary.withOpacity(opacity);
  static Color accentWithOpacity(double opacity) => accent.withOpacity(opacity);
  static Color surfaceWithOpacity(double opacity) =>
      surface.withOpacity(opacity);

  // Cores para diferentes estados de componentes
  static const Color cardBackground = surface;
  static const Color cardBorder = Color(0xFF3A3A3A);
  static const Color divider = Color(0xFF3A3A3A);

  // Cores para ranking
  static const Color gold = Color(0xFFFFD700);
  static const Color silver = Color(0xFFC0C0C0);
  static const Color bronze = Color(0xFFCD7F32);

  // Cores para badges
  static const Color badgeCommon = Color(0xFF6B7280);
  static const Color badgeRare = Color(0xFF3B82F6);
  static const Color badgeEpic = Color(0xFF8B5CF6);
  static const Color badgeLegendary = Color(0xFFF59E0B);
}
