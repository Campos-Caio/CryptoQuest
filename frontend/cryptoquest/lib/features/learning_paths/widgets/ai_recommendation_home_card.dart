import 'package:flutter/material.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';

class AIRecommendationHomeCard extends StatelessWidget {
  final Map<String, dynamic> recommendation;
  final VoidCallback? onTap;

  const AIRecommendationHomeCard({
    Key? key,
    required this.recommendation,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final name = recommendation['name'] as String? ?? 'Trilha Desconhecida';
    final description = recommendation['description'] as String? ?? '';
    final relevanceScore =
        (recommendation['relevance_score'] as num? ?? 0.0).toDouble();

    // Tratar estimated_duration como string ou int
    final estimatedDuration =
        _parseEstimatedDuration(recommendation['estimated_duration']);

    return Card(
      color: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: AppColors.cardBorder, width: 1),
      ),
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Ícone principal (igual aos outros FeatureCards)
              Icon(
                Icons.psychology,
                color: AppColors.accent,
                size: 32,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Row(
                            children: [
                              Text(
                                name,
                                style: Theme.of(context)
                                    .textTheme
                                    .titleMedium
                                    ?.copyWith(
                                      color: AppColors.onSurface,
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: AppColors.accent.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  'IA',
                                  style: TextStyle(
                                    color: AppColors.accent,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.accent.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: AppColors.accent.withOpacity(0.4),
                              width: 1,
                            ),
                          ),
                          child: Text(
                            '${(relevanceScore * 100).toInt()}%',
                            style: TextStyle(
                              color: AppColors.accent,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      description,
                      style: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.copyWith(color: AppColors.onSurfaceVariant),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(
                          Icons.schedule,
                          size: 14,
                          color: AppColors.onSurfaceVariant,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          estimatedDuration,
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(color: AppColors.onSurfaceVariant),
                        ),
                        const SizedBox(width: 16),
                        Icon(
                          Icons.recommend,
                          size: 14,
                          color: AppColors.onSurfaceVariant,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Recomendada',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(color: AppColors.onSurfaceVariant),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                color: AppColors.onSurfaceVariant,
                size: 16,
              ),
            ],
          ),
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
