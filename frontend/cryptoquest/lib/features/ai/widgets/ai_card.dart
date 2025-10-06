import 'package:flutter/material.dart';
import '../theme/ai_colors.dart';

class AICard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final VoidCallback? onTap;
  final bool isElevated;
  final bool hasGlow;
  final Color? backgroundColor;
  final String? title;
  final IconData? titleIcon;
  final Color? titleIconColor;

  const AICard({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.borderRadius = 16.0,
    this.onTap,
    this.isElevated = false,
    this.hasGlow = false,
    this.backgroundColor,
    this.title,
    this.titleIcon,
    this.titleIconColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(borderRadius),
          child: Container(
            padding: padding ?? const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient:
                  backgroundColor != null ? null : AIColors.aiCardGradient,
              color: backgroundColor,
              borderRadius: BorderRadius.circular(borderRadius),
              border: Border.all(
                color: hasGlow
                    ? AIColors.aiPrimary.withOpacity(0.3)
                    : AIColors.aiPrimary.withOpacity(0.1),
                width: hasGlow ? 2 : 1,
              ),
              boxShadow: hasGlow
                  ? AIColors.aiGlowShadow
                  : isElevated
                      ? AIColors.aiElevatedShadow
                      : AIColors.aiCardShadow,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (title != null) ...[
                  _buildTitle(),
                  const SizedBox(height: 16),
                ],
                child,
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTitle() {
    return Row(
      children: [
        if (titleIcon != null) ...[
          Icon(
            titleIcon,
            color: titleIconColor ?? AIColors.aiPrimary,
            size: 24,
          ),
          const SizedBox(width: 8),
        ],
        Text(
          title!,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AIColors.textPrimary,
          ),
        ),
      ],
    );
  }
}

class AIStatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final String? subtitle;
  final VoidCallback? onTap;

  const AIStatCard({
    Key? key,
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
    this.subtitle,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AICard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: color,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    color: AIColors.textSecondary,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(
                    color: AIColors.textPrimary,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    subtitle!,
                    style: TextStyle(
                      color: AIColors.textTertiary,
                      fontSize: 12,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class AIProgressCard extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  final String? description;

  const AIProgressCard({
    Key? key,
    required this.label,
    required this.value,
    required this.color,
    this.description,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AICard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: TextStyle(
                  color: AIColors.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '${(value * 100).toInt()}%',
                style: TextStyle(
                  color: color,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: value,
            backgroundColor: AIColors.cardBackground,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
          if (description != null) ...[
            const SizedBox(height: 8),
            Text(
              description!,
              style: TextStyle(
                color: AIColors.textSecondary,
                fontSize: 12,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class AIRecommendationCard extends StatelessWidget {
  final String title;
  final String type;
  final double relevanceScore;
  final String reasoning;
  final List<String> learningObjectives;
  final VoidCallback? onTap;

  const AIRecommendationCard({
    Key? key,
    required this.title,
    required this.type,
    required this.relevanceScore,
    required this.reasoning,
    required this.learningObjectives,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AICard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      hasGlow: relevanceScore > 0.8,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.star,
                color: AIColors.aiWarning,
                size: 20,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '$type: $title',
                  style: TextStyle(
                    color: AIColors.textPrimary,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AIColors.aiSuccess.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${(relevanceScore * 100).toInt()}%',
                  style: TextStyle(
                    color: AIColors.aiSuccess,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            reasoning,
            style: TextStyle(
              color: AIColors.textSecondary,
              fontSize: 14,
            ),
          ),
          if (learningObjectives.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              'Objetivos de Aprendizado:',
              style: TextStyle(
                color: AIColors.textPrimary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            ...learningObjectives
                .map((objective) => Padding(
                      padding: const EdgeInsets.only(left: 8, bottom: 2),
                      child: Row(
                        children: [
                          Icon(
                            Icons.check_circle_outline,
                            size: 12,
                            color: AIColors.aiSuccess,
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              objective,
                              style: TextStyle(
                                color: AIColors.textTertiary,
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ))
                .toList(),
          ],
        ],
      ),
    );
  }
}
