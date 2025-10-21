import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';
import 'package:cryptoquest/shared/widgets/enhanced_confetti_widget.dart';

/// Tela especializada para conquistas lendárias
///
/// Tela dedicada para celebrar conquistas lendárias
/// com animações especiais e efeitos visuais únicos
class LegendaryAchievementScreen extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;
  final VoidCallback? onViewProfile;
  final VoidCallback? onViewBadges;

  const LegendaryAchievementScreen({
    super.key,
    required this.rewardData,
    this.onContinue,
    this.onViewProfile,
    this.onViewBadges,
  });

  /// Exibe a tela de Legendary Achievement
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
    VoidCallback? onViewBadges,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.9),
      builder: (context) => LegendaryAchievementScreen(
        rewardData: rewardData,
        onContinue: onContinue,
        onViewProfile: onViewProfile,
        onViewBadges: onViewBadges,
      ),
    );
  }

  @override
  State<LegendaryAchievementScreen> createState() =>
      _LegendaryAchievementScreenState();
}

class _LegendaryAchievementScreenState extends State<LegendaryAchievementScreen>
    with TickerProviderStateMixin {
  late EnhancedConfettiController _confettiController;
  late AnimationController _lottieController;
  late AnimationController _shimmerController;
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();

    _confettiController = EnhancedConfettiController();
    _lottieController = AnimationController(vsync: this);
    _shimmerController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );

    _triggerCelebration();
  }

  void _triggerCelebration() {
    // Haptic feedback lendário
    HapticFeedback.heavyImpact();

    // Iniciar animações
    _shimmerController.repeat();
    _pulseController.repeat(reverse: true);

    // Confetti lendário após delay
    Future.delayed(const Duration(milliseconds: 800), () {
      if (mounted) {
        _confettiController.showLegendary();
      }
    });
  }

  @override
  void dispose() {
    _confettiController.dispose();
    _lottieController.dispose();
    _shimmerController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;

    // Tela grande para conquistas lendárias
    final maxHeight = (screenHeight * 0.9).toDouble();
    final maxWidth =
        screenWidth > 600 ? 550.0 : (screenWidth * 0.95).toDouble();

    return Stack(
      children: [
        // Confetti lendário de fundo
        Align(
          alignment: Alignment.topCenter,
          child: EnhancedConfettiWidget(
            controller: _confettiController.controller,
            type: ConfettiType.legendary,
            numberOfParticles: 35,
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
                  color: AppColors.gold.withOpacity(0.4),
                  blurRadius: 30,
                  spreadRadius: 10,
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.6),
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
                        // Animação Lottie lendária
                        _buildLegendaryAnimation(),

                        const SizedBox(height: 32),

                        // Título principal
                        _buildMainTitle(),

                        const SizedBox(height: 24),

                        // Card de conquista lendária
                        _buildLegendaryCard(),

                        const SizedBox(height: 24),

                        // Estatísticas de recompensas
                        if (widget.rewardData.xpGained > 0 ||
                            widget.rewardData.pointsGained > 0)
                          _buildRewardsSection(),

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
                begin: const Offset(0.2, 0.2),
                end: const Offset(1.0, 1.0),
                duration: 800.ms,
                curve: Curves.elasticOut,
              )
              .fadeIn(duration: 500.ms),
        ),
      ],
    );
  }

  /// Animação Lottie lendária
  Widget _buildLegendaryAnimation() {
    return Center(
      child: LottieAnimations.badgeUnlock(
        size: 220,
        controller: _lottieController,
      ),
    ).animate().fadeIn(duration: 500.ms).scale(
          begin: const Offset(0.0, 0.0),
          end: const Offset(1.0, 1.0),
          curve: Curves.elasticOut,
          duration: 1000.ms,
        );
  }

  /// Título principal da tela
  Widget _buildMainTitle() {
    return Column(
      children: [
        Text(
          'CONQUISTA LENDÁRIA!',
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: AppColors.gold,
            letterSpacing: 2,
          ),
        ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.3, end: 0.0),
        const SizedBox(height: 8),
        Text(
          'Você alcançou algo extraordinário!',
          style: TextStyle(
            fontSize: 18,
            color: AppColors.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ).animate().fadeIn(delay: 500.ms).slideY(begin: 0.2, end: 0.0),
      ],
    );
  }

  /// Card de conquista lendária
  Widget _buildLegendaryCard() {
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.gold,
            AppColors.gold.withOpacity(0.8),
            AppColors.primary,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppColors.gold.withOpacity(0.4),
            blurRadius: 20,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Column(
        children: [
          // Ícone lendário animado
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Transform.scale(
                scale: 1.0 + (_pulseController.value * 0.15),
                child: Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: AppColors.white.withOpacity(0.2),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.white.withOpacity(0.5),
                      width: 3,
                    ),
                  ),
                  child: const FaIcon(
                    FontAwesomeIcons.crown,
                    size: 50,
                    color: AppColors.white,
                  ),
                ),
              );
            },
          ).animate().scale(
                begin: const Offset(0.0, 0.0),
                end: const Offset(1.0, 1.0),
                delay: 700.ms,
                curve: Curves.elasticOut,
              ),

          const SizedBox(height: 20),

          // Texto lendário
          Text(
            'LENDÁRIO',
            style: TextStyle(
              fontSize: 36,
              fontWeight: FontWeight.bold,
              color: AppColors.white,
              letterSpacing: 3,
            ),
          ).animate().fadeIn(delay: 900.ms),

          const SizedBox(height: 8),

          Text(
            'Conquista Extraordinária',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.white.withOpacity(0.9),
            ),
          ).animate().fadeIn(delay: 1100.ms),

          const SizedBox(height: 4),

          Text(
            'Você fez história!',
            style: TextStyle(
              fontSize: 14,
              color: AppColors.white.withOpacity(0.8),
            ),
          ).animate().fadeIn(delay: 1300.ms),
        ],
      ),
    )
        .animate()
        .fadeIn(delay: 600.ms)
        .slideY(begin: 0.3, end: 0.0)
        .then()
        .shimmer(
          duration: const Duration(milliseconds: 2000),
          color: AppColors.white.withOpacity(0.3),
        );
  }

  /// Seção de recompensas
  Widget _buildRewardsSection() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.gold.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const FaIcon(
                FontAwesomeIcons.gem,
                size: 24,
                color: AppColors.gold,
              ),
              const SizedBox(width: 12),
              Text(
                'Recompensas Lendárias',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.white,
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // XP ganho
          if (widget.rewardData.xpGained > 0) ...[
            _buildRewardRow(
              icon: FontAwesomeIcons.coins,
              label: 'XP Lendário',
              value: '+${widget.rewardData.xpGained}',
              color: AppColors.success,
              animation: LottieAnimations.coins(size: 24, repeat: true),
            ),
            if (widget.rewardData.pointsGained > 0) const SizedBox(height: 16),
          ],

          // Pontos ganhos
          if (widget.rewardData.pointsGained > 0)
            _buildRewardRow(
              icon: FontAwesomeIcons.star,
              label: 'Pontos Lendários',
              value: '+${widget.rewardData.pointsGained}',
              color: AppColors.gold,
              animation: LottieAnimations.stars(size: 24, repeat: true),
            ),
        ],
      ),
    ).animate().fadeIn(delay: 1500.ms).slideY(begin: 0.2, end: 0.0);
  }

  /// Linha de recompensa
  Widget _buildRewardRow({
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
              delay: 1700.ms,
              curve: Curves.elasticOut,
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
              gradient: LinearGradient(
                colors: [
                  AppColors.gold,
                  AppColors.primary,
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: AppColors.gold.withOpacity(0.4),
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

        // Botões secundários
        if (widget.onViewProfile != null) ...[
          const SizedBox(width: 12),
          _buildSecondaryButton(
            icon: FontAwesomeIcons.user,
            onPressed: widget.onViewProfile!,
            color: AppColors.primary,
          ),
        ],

        if (widget.onViewBadges != null) ...[
          const SizedBox(width: 12),
          _buildSecondaryButton(
            icon: FontAwesomeIcons.trophy,
            onPressed: widget.onViewBadges!,
            color: AppColors.gold,
          ),
        ],
      ],
    ).animate().fadeIn(delay: 2000.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Botão secundário
  Widget _buildSecondaryButton({
    required IconData icon,
    required VoidCallback onPressed,
    required Color color,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: IconButton(
        onPressed: () {
          HapticFeedback.selectionClick();
          Navigator.of(context).pop();
          onPressed();
        },
        icon: FaIcon(icon, size: 20),
        color: color,
      ),
    );
  }
}
