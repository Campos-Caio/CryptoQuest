import 'package:flutter/material.dart';
import '../theme/learning_path_colors.dart';
import 'glassmorphism_card.dart';

class AIRecommendationCard extends StatelessWidget {
  final Map<String, dynamic> recommendation;
  final VoidCallback? onTap;
  final bool showFullReasoning;

  const AIRecommendationCard({
    Key? key,
    required this.recommendation,
    this.onTap,
    this.showFullReasoning = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final name = recommendation['title'] as String? ??
        recommendation['name'] as String? ??
        recommendation['content_id'] as String? ??
        'Conteúdo Desconhecido';
    final description = recommendation['description'] as String? ?? '';
    final difficulty =
        recommendation['difficulty'] as String? ?? 'intermediate';
    final relevanceScore =
        (recommendation['relevance_score'] as num? ?? 0.0).toDouble();
    final reasoning = recommendation['reasoning'] as String? ?? '';

    // Corrigir problema de tipo - tratar estimated_duration como string ou int
    final estimatedDuration =
        _parseEstimatedDuration(recommendation['estimated_duration']);

    return GlassmorphismCard(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      onTap: onTap,
      isElevated: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header com título e dificuldade (seguindo EXATAMENTE o padrão do LearningPathCard)
          Row(
            children: [
              Expanded(
                child: Row(
                  children: [
                    // Badge IA compacto (integrado no título)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 4),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            LearningPathColors.primaryPurple.withOpacity(0.9),
                            LearningPathColors.primaryPurpleLight
                                .withOpacity(0.9),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.psychology,
                            color: Colors.white,
                            size: 14,
                          ),
                          const SizedBox(width: 3),
                          Text(
                            'IA',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        name,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: LearningPathColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              _buildDifficultyChip(difficulty),
              const SizedBox(width: 8),
              _buildRelevanceScore(relevanceScore),
            ],
          ),

          const SizedBox(height: 8),

          // Descrição (seguindo exatamente o padrão do LearningPathCard)
          Text(
            description,
            style: TextStyle(
              fontSize: 14,
              color: LearningPathColors.textSecondary,
              height: 1.4,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),

          const SizedBox(height: 16),

          // Informações da trilha (seguindo EXATAMENTE o padrão do LearningPathCard)
          Row(
            children: [
              Icon(
                Icons.schedule,
                size: 16,
                color: LearningPathColors.textTertiary,
              ),
              const SizedBox(width: 4),
              Text(
                estimatedDuration,
                style: TextStyle(
                  fontSize: 12,
                  color: LearningPathColors.textTertiary,
                ),
              ),
              const SizedBox(width: 16),
              Icon(
                Icons.layers,
                size: 16,
                color: LearningPathColors.textTertiary,
              ),
              const SizedBox(width: 4),
              Text(
                'Recomendada',
                style: TextStyle(
                  fontSize: 12,
                  color: LearningPathColors.textTertiary,
                ),
              ),
            ],
          ),

          // Reasoning (só aparece se showFullReasoning = true)
          if (showFullReasoning && reasoning.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: LearningPathColors.primaryPurple.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: LearningPathColors.primaryPurple.withOpacity(0.2),
                  width: 1,
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.lightbulb_outline,
                    color: LearningPathColors.primaryPurple,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      reasoning,
                      style: TextStyle(
                        color: LearningPathColors.textSecondary,
                        fontSize: 12,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Chip de dificuldade (copiado EXATAMENTE do LearningPathCard)
  Widget _buildDifficultyChip(String difficulty) {
    final chipColor = LearningPathColors.getDifficultyColor(difficulty);
    final difficultyText = LearningPathColors.getDifficultyText(difficulty);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            chipColor.withOpacity(0.2),
            chipColor.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: chipColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        difficultyText,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: chipColor,
        ),
      ),
    );
  }

  /// Score de relevância em formato compacto
  Widget _buildRelevanceScore(double relevanceScore) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: LearningPathColors.successGreen.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: LearningPathColors.successGreen.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        '${(relevanceScore * 100).toInt()}%',
        style: TextStyle(
          color: LearningPathColors.successGreen,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// Trata o campo estimated_duration que pode vir como int ou string
  String _parseEstimatedDuration(dynamic duration) {
    if (duration == null) return 'N/A';

    if (duration is int) {
      return '$duration min';
    } else if (duration is String) {
      // Se já é uma string formatada como "15-20 minutos", retorna como está
      if (duration.contains('min')) {
        return duration;
      }
      // Se é um número em string, adiciona "min"
      if (RegExp(r'^\d+$').hasMatch(duration)) {
        return '$duration min';
      }
      return duration; // Retorna como está se não conseguir processar
    } else {
      return 'N/A';
    }
  }
}
