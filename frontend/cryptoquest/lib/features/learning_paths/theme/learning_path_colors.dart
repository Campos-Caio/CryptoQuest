import 'package:flutter/material.dart';

/// Esquema de cores consistente para o sistema de trilhas de aprendizado
/// Baseado no tema dark do CryptoQuest
class LearningPathColors {
  // Cores principais do tema
  static const Color primaryPurple = Color(0xFF7F5AF0);
  static const Color primaryPurpleLight = Color(0xFF9B7AFF);
  static const Color primaryPurpleDark = Color(0xFF5A3FCC);

  // Cores de fundo
  static const Color darkBackground = Color(0xFF16161A);
  static const Color cardBackground = Color(0xFF242629);
  static const Color cardBackgroundLight = Color(0xFF2A2D3A);

  // Cores de texto
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFF94A1B2);
  static const Color textTertiary = Color(0xFF72757E);

  // Cores de status
  static const Color successGreen = Color(0xFF00D4AA);
  static const Color successGreenLight = Color(0xFF33E0BB);
  static const Color warningOrange = Color(0xFFFFB800);
  static const Color warningOrangeLight = Color(0xFFFFCC33);
  static const Color errorRed = Color(0xFFFF6B6B);
  static const Color errorRedLight = Color(0xFFFF8A8A);

  // Cores de dificuldade
  static const Color difficultyBeginner = Color(0xFF00D4AA);
  static const Color difficultyIntermediate = Color(0xFFFFB800);
  static const Color difficultyAdvanced = Color(0xFFFF6B6B);

  // Cores de progresso
  static const Color progressBackground = Color(0xFF2A2D3A);
  static const Color progressActive = Color(0xFF7F5AF0);
  static const Color progressCompleted = Color(0xFF00D4AA);
  static const Color progressLocked = Color(0xFF72757E);

  // Gradientes
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryPurple, primaryPurpleDark],
  );

  static const LinearGradient successGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [successGreen, Color(0xFF00B894)],
  );

  static const LinearGradient warningGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [warningOrange, Color(0xFFE17055)],
  );

  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [cardBackground, cardBackgroundLight],
  );

  // Sombras
  static List<BoxShadow> get cardShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.1),
          blurRadius: 8,
          offset: const Offset(0, 4),
        ),
        BoxShadow(
          color: primaryPurple.withOpacity(0.05),
          blurRadius: 16,
          offset: const Offset(0, 8),
        ),
      ];

  static List<BoxShadow> get elevatedShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.15),
          blurRadius: 12,
          offset: const Offset(0, 6),
        ),
        BoxShadow(
          color: primaryPurple.withOpacity(0.1),
          blurRadius: 24,
          offset: const Offset(0, 12),
        ),
      ];

  // Métodos utilitários
  static Color getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return difficultyBeginner;
      case 'intermediate':
        return difficultyIntermediate;
      case 'advanced':
        return difficultyAdvanced;
      default:
        return difficultyBeginner;
    }
  }

  static String getDifficultyText(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return 'Iniciante';
      case 'intermediate':
        return 'Intermediário';
      case 'advanced':
        return 'Avançado';
      default:
        return 'Iniciante';
    }
  }
}
