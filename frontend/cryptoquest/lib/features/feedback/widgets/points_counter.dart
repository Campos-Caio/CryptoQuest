import 'package:flutter/material.dart';
import 'package:animated_flip_counter/animated_flip_counter.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';

/// Widget contador de pontos com animação
///
/// Exibe pontos ganhos com animação estilo flip/odômetro
/// e efeitos visuais para destacar a conquista
class PointsCounter extends StatelessWidget {
  final int points;
  final String label;
  final IconData icon;
  final Color? color;
  final bool showPrefix;

  const PointsCounter({
    super.key,
    required this.points,
    this.label = 'Pontos',
    this.icon = Icons.stars,
    this.color,
    this.showPrefix = true,
  });

  @override
  Widget build(BuildContext context) {
    final displayColor = color ?? AppColors.gold;
    final gradient = color == AppColors.gold
        ? const LinearGradient(
            colors: [
              Color(0xFF8B6914),
              Color(0xFFB8860B)
            ], // Dourado mais suave
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          )
        : AppColors.primaryGradient;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: displayColor.withOpacity(0.4),
            blurRadius: 15,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Ícone animado
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: AppColors.white,
              size: 24,
            ),
          )
              .animate(
                onPlay: (controller) => controller.repeat(
                  reverse: true,
                  period: const Duration(milliseconds: 1000),
                  min: 0,
                  max: 3, // Limitar a 3 ciclos
                ),
              )
              .scale(
                begin: const Offset(1.0, 1.0),
                end: const Offset(1.15, 1.15), // Reduzir intensidade
              )
              .then()
              .shimmer(
                duration: const Duration(milliseconds: 1500),
                color: Colors.white.withOpacity(0.3), // Reduzir intensidade
              ),

          const SizedBox(width: 12),

          // Contador animado
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 14,
                  color: AppColors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  if (showPrefix)
                    Text(
                      '+',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: AppColors.white,
                      ),
                    ),
                  AnimatedFlipCounter(
                    value: points,
                    duration: const Duration(milliseconds: 1000),
                    textStyle: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: AppColors.white,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms).scale(
          begin: const Offset(0.8, 0.8),
          end: const Offset(1.0, 1.0),
          duration: 400.ms,
          curve: Curves.elasticOut,
        );
  }
}

/// Widget simplificado para exibir múltiplos contadores em linha
class CompactPointsCounter extends StatelessWidget {
  final int points;
  final int xp;
  final IconData pointsIcon;
  final IconData xpIcon;

  const CompactPointsCounter({
    super.key,
    required this.points,
    required this.xp,
    this.pointsIcon = Icons.stars,
    this.xpIcon = Icons.bolt,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildCompactCounter(
          value: points,
          icon: pointsIcon,
          color: Colors.amber,
        ),
        Container(
          width: 1,
          height: 30,
          color: AppColors.surfaceVariant,
        ),
        _buildCompactCounter(
          value: xp,
          icon: xpIcon,
          color: const Color(0xFF4A7C59), // Verde suave
        ),
      ],
    );
  }

  Widget _buildCompactCounter({
    required int value,
    required IconData icon,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 6),
        AnimatedFlipCounter(
          value: value,
          duration: const Duration(milliseconds: 800),
          prefix: '+',
          textStyle: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
