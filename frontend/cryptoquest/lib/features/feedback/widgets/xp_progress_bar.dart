import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';

/// Widget de barra de progresso de XP com animação
///
/// Exibe o progresso de XP do usuário com animação suave
/// quando o valor muda, incluindo indicadores visuais de ganho
class XPProgressBar extends StatefulWidget {
  final int previousXP;
  final int currentXP;
  final int xpForNextLevel;
  final int xpGained;
  final Duration animationDuration;

  const XPProgressBar({
    super.key,
    required this.previousXP,
    required this.currentXP,
    required this.xpForNextLevel,
    required this.xpGained,
    this.animationDuration = const Duration(milliseconds: 1500),
  });

  @override
  State<XPProgressBar> createState() => _XPProgressBarState();
}

class _XPProgressBarState extends State<XPProgressBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  late Animation<int> _xpCountAnimation;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    final previousProgress = widget.previousXP / widget.xpForNextLevel;
    final currentProgress = widget.currentXP / widget.xpForNextLevel;

    _progressAnimation = Tween<double>(
      begin: previousProgress,
      end: currentProgress,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    _xpCountAnimation = IntTween(
      begin: widget.previousXP,
      end: widget.currentXP,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: AppColors.primary.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Experiência',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.onSurface,
                    ),
                  ),
                  if (widget.xpGained > 0)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            Color(0xFF2D5A3D),
                            Color(0xFF4A7C59)
                          ], // Verde mais suave
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        '+${widget.xpGained} XP',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: AppColors.white,
                        ),
                      ),
                    )
                        .animate(
                          onPlay: (controller) => controller.repeat(
                            reverse: true,
                            period: const Duration(milliseconds: 800),
                            min: 0,
                            max: 3, // Limitar a 3 ciclos
                          ),
                        )
                        .scale(
                          begin: const Offset(1.0, 1.0),
                          end: const Offset(1.08, 1.08), // Reduzir intensidade
                        ),
                ],
              ),
              const SizedBox(height: 12),

              // Barra de progresso
              Stack(
                children: [
                  // Barra de fundo
                  Container(
                    height: 12,
                    decoration: BoxDecoration(
                      color: AppColors.surfaceVariant,
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),

                  // Barra de progresso animada
                  FractionallySizedBox(
                    widthFactor: _progressAnimation.value.clamp(0.0, 1.0),
                    child: Container(
                      height: 12,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            Color(0xFF2D5A3D),
                            Color(0xFF4A7C59)
                          ], // Verde mais suave
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(6),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF2D5A3D).withOpacity(0.4),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Texto de XP
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${_xpCountAnimation.value} / ${widget.xpForNextLevel} XP',
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.onSurfaceVariant,
                    ),
                  ),
                  Text(
                    '${(_progressAnimation.value * 100).toInt()}%',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
