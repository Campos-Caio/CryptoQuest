import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';
import 'package:cryptoquest/shared/widgets/enhanced_confetti_widget.dart';

/// Tela especializada para Level Up
///
/// Tela dedicada para celebrar a subida de nível do usuário
/// com animações especiais e layout otimizado
class LevelUpScreen extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;
  final VoidCallback? onViewProfile;

  const LevelUpScreen({
    super.key,
    required this.rewardData,
    this.onContinue,
    this.onViewProfile,
  });

  /// Exibe a tela de Level Up
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.8),
      builder: (context) => LevelUpScreen(
        rewardData: rewardData,
        onContinue: onContinue,
        onViewProfile: onViewProfile,
      ),
    );
  }

  @override
  State<LevelUpScreen> createState() => _LevelUpScreenState();
}

class _LevelUpScreenState extends State<LevelUpScreen>
    with TickerProviderStateMixin {
  late EnhancedConfettiController _confettiController;
  late AnimationController _lottieController;
  late AnimationController _levelAnimationController;

  @override
  void initState() {
    super.initState();

    _confettiController = EnhancedConfettiController();
    _lottieController = AnimationController(vsync: this);
    _levelAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _triggerCelebration();
  }

  void _triggerCelebration() {
    // Haptic feedback forte para level up
    HapticFeedback.heavyImpact();

    // Iniciar animações
    _levelAnimationController.forward();

    // Confetti após delay
    Future.delayed(const Duration(milliseconds: 800), () {
      if (mounted) {
        _confettiController.showLevelUp();
      }
    });
  }

  @override
  void dispose() {
    _confettiController.dispose();
    _lottieController.dispose();
    _levelAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;

    // Tela maior para level up (90% da altura)
    final maxHeight = (screenHeight * 0.9).toDouble();
    final maxWidth =
        screenWidth > 600 ? 500.0 : (screenWidth * 0.95).toDouble();

    return Stack(
      children: [
        // Confetti de fundo
        Align(
          alignment: Alignment.topCenter,
          child: EnhancedConfettiWidget(
            controller: _confettiController.controller,
            type: ConfettiType.levelUp,
            numberOfParticles: 30,
          ),
        ),

        // Conteúdo principal
        Center(
          child: Container(
            constraints: BoxConstraints(
              maxHeight: maxHeight,
              maxWidth: maxWidth,
            ),
            margin: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(32),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.3),
                  blurRadius: 30,
                  spreadRadius: 10,
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.5),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Conteúdo scrollável
                Flexible(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Animação Lottie de Level Up
                        _buildLevelUpAnimation(),

                        const SizedBox(height: 32),

                        // Título principal
                        _buildMainTitle(),

                        const SizedBox(height: 24),

                        // Cards de nível anterior e atual
                        _buildLevelCards(),

                        const SizedBox(height: 32),

                        // Estatísticas de progresso
                        _buildProgressStats(),

                        const SizedBox(height: 24),

                        // Botões de ação
                        _buildActionButtons(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          )
              .animate()
              .scale(
                begin: const Offset(0.3, 0.3),
                end: const Offset(1.0, 1.0),
                duration: 600.ms,
                curve: Curves.elasticOut,
              )
              .fadeIn(duration: 400.ms),
        ),
      ],
    );
  }

  /// Animação Lottie de Level Up
  Widget _buildLevelUpAnimation() {
    return Center(
      child: LottieAnimations.levelUp(
        size: 200,
        controller: _lottieController,
      ),
    ).animate().fadeIn(duration: 500.ms).scale(
          begin: const Offset(0.5, 0.5),
          end: const Offset(1.0, 1.0),
          curve: Curves.elasticOut,
          duration: 800.ms,
        );
  }

  /// Título principal da tela
  Widget _buildMainTitle() {
    return Column(
      children: [
        Text(
          'LEVEL UP!',
          style: TextStyle(
            fontSize: 36,
            fontWeight: FontWeight.bold,
            color: AppColors.white,
            letterSpacing: 2,
          ),
        ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.3, end: 0.0),
        const SizedBox(height: 8),
        Text(
          'Parabéns! Você subiu de nível!',
          style: TextStyle(
            fontSize: 18,
            color: AppColors.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ).animate().fadeIn(delay: 500.ms).slideY(begin: 0.2, end: 0.0),
      ],
    );
  }

  /// Cards mostrando nível anterior e atual
  Widget _buildLevelCards() {
    return Row(
      children: [
        // Nível anterior
        Expanded(
          child: _buildLevelCard(
            level: widget.rewardData.previousLevel,
            label: 'Nível Anterior',
            isCurrent: false,
          ),
        ),

        const SizedBox(width: 16),

        // Seta de progresso
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            gradient: AppColors.primaryGradient,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withOpacity(0.4),
                blurRadius: 12,
                spreadRadius: 2,
              ),
            ],
          ),
          child: const FaIcon(
            FontAwesomeIcons.arrowRight,
            color: AppColors.white,
            size: 20,
          ),
        ).animate().scale(
              begin: const Offset(0.0, 0.0),
              end: const Offset(1.0, 1.0),
              delay: 800.ms,
              curve: Curves.elasticOut,
            ),

        const SizedBox(width: 16),

        // Nível atual
        Expanded(
          child: _buildLevelCard(
            level: widget.rewardData.currentLevel,
            label: 'Novo Nível',
            isCurrent: true,
          ),
        ),
      ],
    ).animate().fadeIn(delay: 700.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Card individual de nível
  Widget _buildLevelCard({
    required int level,
    required String label,
    required bool isCurrent,
  }) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: isCurrent ? AppColors.primaryGradient : null,
        color: isCurrent ? null : AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isCurrent
              ? AppColors.primary.withOpacity(0.5)
              : AppColors.primary.withOpacity(0.3),
          width: 2,
        ),
        boxShadow: isCurrent
            ? [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.3),
                  blurRadius: 15,
                  spreadRadius: 3,
                ),
              ]
            : null,
      ),
      child: Column(
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: isCurrent
                  ? AppColors.white.withOpacity(0.9)
                  : AppColors.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          AnimatedBuilder(
            animation: _levelAnimationController,
            builder: (context, child) {
              return Transform.scale(
                scale: isCurrent
                    ? 1.0 + (_levelAnimationController.value * 0.2)
                    : 1.0,
                child: Text(
                  '$level',
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: isCurrent ? AppColors.white : AppColors.primary,
                  ),
                ),
              );
            },
          ),
        ],
      ),
    ).animate().scale(
          begin: const Offset(0.8, 0.8),
          end: const Offset(1.0, 1.0),
          delay: isCurrent ? 1000.ms : 900.ms,
          curve: Curves.elasticOut,
        );
  }

  /// Estatísticas de progresso
  Widget _buildProgressStats() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.primary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          // XP ganho
          _buildStatRow(
            icon: FontAwesomeIcons.coins,
            label: 'XP Ganho',
            value: '+${widget.rewardData.xpGained}',
            color: AppColors.success,
            animation: LottieAnimations.coins(size: 24, repeat: true),
          ),

          const SizedBox(height: 16),

          // Pontos ganhos
          if (widget.rewardData.pointsGained > 0) ...[
            _buildStatRow(
              icon: FontAwesomeIcons.star,
              label: 'Pontos Ganhos',
              value: '+${widget.rewardData.pointsGained}',
              color: AppColors.gold,
              animation: LottieAnimations.stars(size: 24, repeat: true),
            ),
            const SizedBox(height: 16),
          ],

          // Progresso para próximo nível
          _buildNextLevelProgress(),
        ],
      ),
    ).animate().fadeIn(delay: 1200.ms).slideY(begin: 0.2, end: 0.0);
  }

  /// Linha de estatística
  Widget _buildStatRow({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
    Widget? animation,
  }) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(12),
          ),
          child: animation ??
              FaIcon(
                icon,
                color: color,
                size: 20,
              ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 16,
              color: AppColors.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ).animate().scale(
              begin: const Offset(0.0, 0.0),
              end: const Offset(1.0, 1.0),
              delay: 1500.ms,
              curve: Curves.elasticOut,
            ),
      ],
    );
  }

  /// Progresso para próximo nível
  Widget _buildNextLevelProgress() {
    final nextLevelXP = _calculateXPForNextLevel();
    final progress =
        (widget.rewardData.currentXP / nextLevelXP).clamp(0.0, 1.0);
    final percentage = (progress * 100).toInt();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Progresso para Nível ${widget.rewardData.currentLevel + 1}',
              style: TextStyle(
                fontSize: 14,
                color: AppColors.onSurfaceVariant,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              '$percentage%',
              style: TextStyle(
                fontSize: 14,
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Stack(
          children: [
            Container(
              height: 8,
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            FractionallySizedBox(
              widthFactor: progress,
              child: Container(
                height: 8,
                decoration: BoxDecoration(
                  gradient: AppColors.primaryGradient,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ).animate().scaleX(
                  duration: 1500.ms,
                  delay: 1800.ms,
                  curve: Curves.easeOutCubic,
                ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          '${widget.rewardData.currentXP} / $nextLevelXP XP',
          style: TextStyle(
            fontSize: 12,
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  /// Botões de ação
  Widget _buildActionButtons() {
    return Row(
      children: [
        // Botão principal (Continuar)
        Expanded(
          flex: 2,
          child: Container(
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.4),
                  blurRadius: 15,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: () {
                HapticFeedback.lightImpact();
                Navigator.of(context).pop();
                widget.onContinue?.call();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                foregroundColor: AppColors.white,
                padding: const EdgeInsets.symmetric(vertical: 18),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: const Text(
                'Continuar',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ),

        // Botão de perfil (se disponível)
        if (widget.onViewProfile != null) ...[
          const SizedBox(width: 12),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: AppColors.primary.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: IconButton(
              onPressed: () {
                HapticFeedback.selectionClick();
                Navigator.of(context).pop();
                widget.onViewProfile?.call();
              },
              icon: const FaIcon(FontAwesomeIcons.user, size: 20),
              color: AppColors.primary,
              tooltip: 'Ver Perfil',
            ),
          ),
        ],
      ],
    ).animate().fadeIn(delay: 2000.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Calcula XP necessário para próximo nível
  int _calculateXPForNextLevel() {
    final currentLevel = widget.rewardData.currentLevel;
    final currentXP = widget.rewardData.currentXP;

    final levelRequirements = {
      1: 0,
      2: 500,
      3: 1000,
      4: 1500,
      5: 2000,
      6: 2500,
      7: 3000,
      8: 3500,
      9: 4000,
      10: 4500,
      11: 5250,
      12: 6000,
      13: 6750,
      14: 7500,
      15: 8250,
      16: 9000,
      17: 9750,
      18: 10500,
      19: 11250,
      20: 12000,
      21: 13000,
      22: 14000,
      23: 15000,
      24: 16000,
      25: 17000,
    };

    int nextLevel = currentLevel + 1;
    while (nextLevel <= 25 && levelRequirements[nextLevel]! <= currentXP) {
      nextLevel++;
    }

    if (nextLevel > 25) {
      return currentXP;
    }

    return levelRequirements[nextLevel]!;
  }
}
