import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

abstract class AppTheme {
  static ThemeData appTheme = ThemeData.dark().copyWith(
    // Cores principais
    primaryColor: AppColors.primary,
    scaffoldBackgroundColor: AppColors.background,
    cardColor: AppColors.surface,

    // AppBar
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.primary,
      foregroundColor: AppColors.onPrimary,
      elevation: 0,
      centerTitle: true,
    ),

    // Texto
    textTheme: GoogleFonts.poppinsTextTheme(
      ThemeData.dark().textTheme,
    ).copyWith(
      headlineLarge: GoogleFonts.poppins(
        color: AppColors.onBackground,
        fontSize: 32,
        fontWeight: FontWeight.bold,
      ),
      headlineMedium: GoogleFonts.poppins(
        color: AppColors.onBackground,
        fontSize: 24,
        fontWeight: FontWeight.bold,
      ),
      headlineSmall: GoogleFonts.poppins(
        color: AppColors.onBackground,
        fontSize: 20,
        fontWeight: FontWeight.w600,
      ),
      bodyLarge: GoogleFonts.poppins(
        color: AppColors.onBackground,
        fontSize: 16,
      ),
      bodyMedium: GoogleFonts.poppins(
        color: AppColors.onSurface,
        fontSize: 14,
      ),
      bodySmall: GoogleFonts.poppins(
        color: AppColors.onSurfaceVariant,
        fontSize: 12,
      ),
    ),

    // Cards
    cardTheme: CardThemeData(
      color: AppColors.cardBackground,
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: AppColors.cardBorder, width: 1),
      ),
    ),

    // Inputs
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surface,
      suffixIconColor: AppColors.primary,
      prefixIconColor: AppColors.primary,
      enabledBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.cardBorder),
        borderRadius: BorderRadius.circular(12),
      ),
      focusedBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.primary, width: 2),
        borderRadius: BorderRadius.circular(12),
      ),
      errorBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.error),
        borderRadius: BorderRadius.circular(12),
      ),
      hintStyle: const TextStyle(color: AppColors.onSurfaceVariant),
      labelStyle: const TextStyle(color: AppColors.onSurfaceVariant),
    ),

    // Botões
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      ),
    ),

    // Floating Action Button
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: AppColors.accent,
      foregroundColor: AppColors.black,
      elevation: 6,
    ),

    // Divider
    dividerTheme: const DividerThemeData(
      color: AppColors.divider,
      thickness: 1,
    ),

    // Progress Indicator
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: AppColors.accent,
      linearTrackColor: AppColors.surfaceVariant,
      circularTrackColor: AppColors.surfaceVariant,
    ),
  );
}
