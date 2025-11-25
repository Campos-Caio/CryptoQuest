import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';

/// Tela especializada para conquistas menores
///
/// Tela compacta para conquistas menores com
/// feedback visual simples e eficiente
class MinorAchievementScreen extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;

  const MinorAchievementScreen({
    super.key,
    required this.rewardData,
    this.onContinue,
  });

  /// Exibe a tela de Minor Achievement
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.5),
      builder: (context) => MinorAchievementScreen(
        rewardData: rewardData,
        onContinue: onContinue,
      ),
    );
  }

  @override
  State<MinorAchievementScreen> createState() => _MinorAchievementScreenState();
}

class _MinorAchievementScreenState extends State<MinorAchievementScreen>
    with TickerProviderStateMixin {
  late AnimationController _lottieController;

  @override
  void initState() {
    super.initState();

    _lottieController = AnimationController(vsync: this);

    _triggerCelebration();
  }

  void _triggerCelebration() {
    // Haptic feedback leve para conquistas menores
    HapticFeedback.lightImpact();
  }

  @override
  void dispose() {
    _lottieController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;

    // Tela compacta para conquistas menores
    final maxHeight = (screenHeight * 0.6).toDouble();
    final maxWidth =
        screenWidth > 600 ? 400.0 : (screenWidth * 0.85).toDouble();

    return Center(
      child: Container(
        constraints: BoxConstraints(
          maxHeight: maxHeight,
          maxWidth: maxWidth,
        ),
        margin: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.background,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withOpacity(0.2),
              blurRadius: 15,
              spreadRadius: 3,
            ),
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 10,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Conteúdo principal
            Flexible(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Animação Lottie simples
                    _buildSimpleAnimation(),

                    const SizedBox(height: 20),

                    // Título principal
                    _buildMainTitle(),

                    const SizedBox(height: 16),

                    // Card de conquista
                    _buildAchievementCard(),

                    const SizedBox(height: 20),

                    // Botão de ação
                    _buildActionButton(),
                  ],
                ),
              ),
            ),
          ],
        ),
      )
          .animate()
          .scale(
            begin: const Offset(0.7, 0.7),
            end: const Offset(1.0, 1.0),
            duration: 300.ms,
            curve: Curves.easeOut,
          )
          .fadeIn(duration: 200.ms),
    );
  }

  /// Animação Lottie simples
  Widget _buildSimpleAnimation() {
    return Center(
      child: LottieAnimations.successCheck(
        size: 80,
        controller: _lottieController,
      ),
    ).animate().fadeIn(duration: 200.ms).scale(
          begin: const Offset(0.5, 0.5),
          end: const Offset(1.0, 1.0),
          curve: Curves.easeOut,
          duration: 400.ms,
        );
  }

  /// Título principal da tela
  Widget _buildMainTitle() {
    return Column(
      children: [
        Text(
          'Conquista!',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: AppColors.white,
          ),
        ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0.0),
        const SizedBox(height: 4),
        Text(
          'Bom trabalho!',
          style: TextStyle(
            fontSize: 14,
            color: AppColors.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1, end: 0.0),
      ],
    );
  }

  /// Card de conquista
  Widget _buildAchievementCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.primary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          // Estatísticas de recompensas
          if (widget.rewardData.xpGained > 0 ||
              widget.rewardData.pointsGained > 0) ...[
            if (widget.rewardData.xpGained > 0)
              _buildRewardRow(
                icon: FontAwesomeIcons.coins,
                label: 'XP',
                value: '+${widget.rewardData.xpGained}',
                color: AppColors.success,
              ),
            if (widget.rewardData.xpGained > 0 &&
                widget.rewardData.pointsGained > 0)
              const SizedBox(height: 12),
            if (widget.rewardData.pointsGained > 0)
              _buildRewardRow(
                icon: FontAwesomeIcons.star,
                label: 'Pontos',
                value: '+${widget.rewardData.pointsGained}',
                color: AppColors.gold,
              ),
          ] else ...[
            // Mensagem padrão se não houver recompensas
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const FaIcon(
                  FontAwesomeIcons.check,
                  size: 20,
                  color: AppColors.success,
                ),
                const SizedBox(width: 8),
                Text(
                  'Missão concluída!',
                  style: TextStyle(
                    fontSize: 16,
                    color: AppColors.onSurfaceVariant,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0.0);
  }

  /// Linha de recompensa
  Widget _buildRewardRow({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Row(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(10),
          ),
          child: FaIcon(
            icon,
            color: color,
            size: 16,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ).animate().scale(
              begin: const Offset(0.0, 0.0),
              end: const Offset(1.0, 1.0),
              delay: 400.ms,
              curve: Curves.elasticOut,
            ),
      ],
    );
  }

  /// Botão de ação
  Widget _buildActionButton() {
    return Container(
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
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
          padding: const EdgeInsets.symmetric(vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: const Text(
          'Continuar',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 500.ms).slideY(begin: 0.2, end: 0.0);
  }
}
