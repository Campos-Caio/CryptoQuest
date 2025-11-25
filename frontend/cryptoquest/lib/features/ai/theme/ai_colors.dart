import 'package:flutter/material.dart';

/// Esquema de cores específico para o sistema de IA
/// Baseado no tema dark do CryptoQuest com elementos futuristas
class AIColors {
  // Cores principais da IA
  static const Color aiPrimary = Color(0xFF00D4AA);
  static const Color aiPrimaryLight = Color(0xFF33E0BB);
  static const Color aiPrimaryDark = Color(0xFF00B894);

  // Cores secundárias
  static const Color aiSecondary = Color(0xFF7F5AF0);
  static const Color aiSecondaryLight = Color(0xFF9B7AFF);
  static const Color aiSecondaryDark = Color(0xFF5A3FCC);

  // Cores de fundo
  static const Color darkBackground = Color(0xFF16161A);
  static const Color cardBackground = Color(0xFF242629);
  static const Color cardBackgroundLight = Color(0xFF2A2D3A);

  // Cores de texto
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFF94A1B2);
  static const Color textTertiary = Color(0xFF72757E);

  // Cores de status específicas da IA
  static const Color aiSuccess = Color(0xFF00D4AA);
  static const Color aiWarning = Color(0xFFFFB800);
  static const Color aiError = Color(0xFFFF6B6B);
  static const Color aiInfo = Color(0xFF7F5AF0);

  // Cores de proficiência
  static const Color proficiencyHigh = Color(0xFF00D4AA);
  static const Color proficiencyMedium = Color(0xFFFFB800);
  static const Color proficiencyLow = Color(0xFFFF6B6B);

  // Cores de estilo de aprendizado
  static const Color visualLearner = Color(0xFF00D4AA);
  static const Color auditoryLearner = Color(0xFF7F5AF0);
  static const Color kinestheticLearner = Color(0xFFFF6B6B);
  static const Color mixedLearner = Color(0xFFFFB800);

  // Cores de engajamento
  static const Color highEngagement = Color(0xFF00D4AA);
  static const Color mediumEngagement = Color(0xFFFFB800);
  static const Color lowEngagement = Color(0xFFFF6B6B);

  // Gradientes específicos da IA
  static const LinearGradient aiPrimaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [aiPrimary, aiPrimaryDark],
  );

  static const LinearGradient aiSecondaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [aiSecondary, aiSecondaryDark],
  );

  static const LinearGradient aiCardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF242629),
      Color(0xFF2A2D3A),
    ],
  );

  static const LinearGradient aiGlowGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF00D4AA),
      Color(0xFF7F5AF0),
    ],
  );

  // Sombras específicas da IA
  static List<BoxShadow> get aiCardShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.1),
          blurRadius: 8,
          offset: const Offset(0, 4),
        ),
        BoxShadow(
          color: aiPrimary.withOpacity(0.05),
          blurRadius: 16,
          offset: const Offset(0, 8),
        ),
      ];

  static List<BoxShadow> get aiElevatedShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.15),
          blurRadius: 12,
          offset: const Offset(0, 6),
        ),
        BoxShadow(
          color: aiPrimary.withOpacity(0.1),
          blurRadius: 24,
          offset: const Offset(0, 12),
        ),
      ];

  static List<BoxShadow> get aiGlowShadow => [
        BoxShadow(
          color: aiPrimary.withOpacity(0.3),
          blurRadius: 20,
          offset: const Offset(0, 0),
        ),
        BoxShadow(
          color: aiSecondary.withOpacity(0.2),
          blurRadius: 40,
          offset: const Offset(0, 0),
        ),
      ];

  // Métodos utilitários
  static Color getProficiencyColor(double proficiency) {
    if (proficiency >= 0.8) return proficiencyHigh;
    if (proficiency >= 0.5) return proficiencyMedium;
    return proficiencyLow;
  }

  static Color getEngagementColor(double engagement) {
    if (engagement >= 0.8) return highEngagement;
    if (engagement >= 0.5) return mediumEngagement;
    return lowEngagement;
  }

  static Color getLearningStyleColor(String style) {
    switch (style.toLowerCase()) {
      case 'visual':
        return visualLearner;
      case 'auditory':
        return auditoryLearner;
      case 'kinesthetic':
        return kinestheticLearner;
      case 'mixed':
        return mixedLearner;
      default:
        return aiInfo;
    }
  }

  static String getProficiencyText(double proficiency) {
    if (proficiency >= 0.8) return 'Alto';
    if (proficiency >= 0.5) return 'Médio';
    return 'Baixo';
  }

  static String getEngagementText(double engagement) {
    if (engagement >= 0.8) return 'Alto';
    if (engagement >= 0.5) return 'Médio';
    return 'Baixo';
  }

  static String getLearningStyleText(String style) {
    switch (style.toLowerCase()) {
      case 'visual':
        return 'Aprendiz Visual';
      case 'auditory':
        return 'Aprendiz Auditivo';
      case 'kinesthetic':
        return 'Aprendiz Cinestésico';
      case 'mixed':
        return 'Aprendiz Misto';
      case 'new_learner':
        return 'Novo Aprendiz';
      case 'fast_learner':
        return 'Aprendiz Rápido';
      case 'methodical_learner':
        return 'Aprendiz Metódico';
      case 'visual_learner':
        return 'Aprendiz Visual';
      case 'auditory_learner':
        return 'Aprendiz Auditivo';
      case 'mixed_learner':
        return 'Aprendiz Misto';
      default:
        return 'Analisando...';
    }
  }

  static IconData getLearningStyleIcon(String style) {
    switch (style.toLowerCase()) {
      case 'visual':
      case 'visual_learner':
        return Icons.visibility;
      case 'auditory':
      case 'auditory_learner':
        return Icons.hearing;
      case 'kinesthetic':
        return Icons.touch_app;
      case 'mixed':
      case 'mixed_learner':
        return Icons.psychology;
      case 'new_learner':
        return Icons.school;
      case 'fast_learner':
        return Icons.flash_on;
      case 'methodical_learner':
        return Icons.timeline;
      default:
        return Icons.help_outline;
    }
  }
}
