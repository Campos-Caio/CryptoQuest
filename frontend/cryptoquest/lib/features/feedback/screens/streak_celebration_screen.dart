import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';
import 'package:cryptoquest/shared/widgets/enhanced_confetti_widget.dart';

/// Tela especializada para celebração de sequência
///
/// Tela dedicada para celebrar sequências consecutivas
/// com animações de fogo e efeitos especiais
class StreakCelebrationScreen extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;
  final VoidCallback? onViewProfile;

  const StreakCelebrationScreen({
    super.key,
    required this.rewardData,
    this.onContinue,
    this.onViewProfile,
  });

  /// Exibe a tela de Streak Celebration
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.7),
      builder: (context) => StreakCelebrationScreen(
        rewardData: rewardData,
        onContinue: onContinue,
        onViewProfile: onViewProfile,
      ),
    );
  }

  @override
  State<StreakCelebrationScreen> createState() =>
      _StreakCelebrationScreenState();
}

class _StreakCelebrationScreenState extends State<StreakCelebrationScreen>
    with TickerProviderStateMixin {
  late EnhancedConfettiController _confettiController;
  late AnimationController _lottieController;
  late AnimationController _fireController;

  @override
  void initState() {
    super.initState();

    _confettiController = EnhancedConfettiController();
    _lottieController = AnimationController(vsync: this);
    _fireController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _triggerCelebration();
  }

  void _triggerCelebration() {
    final days = widget.rewardData.streakDays;

    // Haptic feedback baseado na sequência
    if (days >= 30) {
      HapticFeedback.heavyImpact();
    } else if (days >= 7) {
      HapticFeedback.mediumImpact();
    } else {
      HapticFeedback.lightImpact();
    }

    // Iniciar animação de fogo
    _fireController.repeat();

    // Confetti para sequências longas
    if (days >= 7) {
      Future.delayed(const Duration(milliseconds: 500), () {
        if (mounted) {
          _confettiController.showStandard();
        }
      });
    }
  }

  @override
  void dispose() {
    _confettiController.dispose();
    _lottieController.dispose();
    _fireController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;

    final days = widget.rewardData.streakDays;
    final maxHeight = days >= 30
        ? (screenHeight * 0.85).toDouble()
        : (screenHeight * 0.75).toDouble();
    final maxWidth = screenWidth > 600 ? 450.0 : (screenWidth * 0.9).toDouble();

    return Stack(
      children: [
        // Confetti de fundo (apenas para sequências longas)
        if (days >= 7)
          Align(
            alignment: Alignment.topCenter,
            child: EnhancedConfettiWidget(
              controller: _confettiController.controller,
              type: ConfettiType.standard,
              numberOfParticles: 20,
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
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.orange.withOpacity(0.3),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.4),
                  blurRadius: 15,
                  spreadRadius: 3,
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Conteúdo scrollável
                Flexible(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Animação Lottie de Fogo
                        _buildFireAnimation(),

                        const SizedBox(height: 24),

                        // Título principal
                        _buildMainTitle(),

                        const SizedBox(height: 20),

                        // Card de sequência principal
                        _buildStreakCard(),

                        const SizedBox(height: 20),

                        // Estatísticas de recompensas
                        if (widget.rewardData.xpGained > 0 ||
                            widget.rewardData.pointsGained > 0)
                          _buildRewardsSection(),

                        const SizedBox(height: 20),

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
                begin: const Offset(0.4, 0.4),
                end: const Offset(1.0, 1.0),
                duration: 500.ms,
                curve: Curves.elasticOut,
              )
              .fadeIn(duration: 300.ms),
        ),
      ],
    );
  }

  /// Animação Lottie de Fogo
  Widget _buildFireAnimation() {
    return Center(
      child: LottieAnimations.fireStreak(
        size: 160,
      ),
    ).animate().fadeIn(duration: 300.ms).scale(
          begin: const Offset(0.3, 0.3),
          end: const Offset(1.0, 1.0),
          curve: Curves.elasticOut,
          duration: 700.ms,
        );
  }

  /// Título principal da tela
  Widget _buildMainTitle() {
    final days = widget.rewardData.streakDays;
    final title = _getStreakTitle(days);
    final subtitle = _getStreakSubtitle(days);

    return Column(
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: AppColors.white,
            letterSpacing: 1,
          ),
        ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.3, end: 0.0),
        const SizedBox(height: 8),
        Text(
          subtitle,
          style: TextStyle(
            fontSize: 16,
            color: AppColors.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2, end: 0.0),
      ],
    );
  }

  /// Card de sequência principal
  Widget _buildStreakCard() {
    final days = widget.rewardData.streakDays;
    final streakColor = _getStreakColor(days);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            streakColor,
            streakColor.withOpacity(0.7),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: streakColor.withOpacity(0.3),
            blurRadius: 15,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        children: [
          // Ícone de fogo animado
          AnimatedBuilder(
            animation: _fireController,
            builder: (context, child) {
              return Transform.scale(
                scale: 1.0 + (_fireController.value * 0.1),
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppColors.white.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const FaIcon(
                    FontAwesomeIcons.fire,
                    size: 40,
                    color: AppColors.white,
                  ),
                ),
              );
            },
          ).animate().scale(
                begin: const Offset(0.0, 0.0),
                end: const Offset(1.0, 1.0),
                delay: 600.ms,
                curve: Curves.elasticOut,
              ),

          const SizedBox(height: 16),

          // Número de dias
          Text(
            '$days',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.bold,
              color: AppColors.white,
            ),
          ).animate().fadeIn(delay: 800.ms),

          const SizedBox(height: 8),

          // Texto de sequência
          Text(
            _getStreakText(days),
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.white,
            ),
          ).animate().fadeIn(delay: 1000.ms),

          const SizedBox(height: 4),

          Text(
            'dias consecutivos!',
            style: TextStyle(
              fontSize: 14,
              color: AppColors.white.withOpacity(0.8),
            ),
          ).animate().fadeIn(delay: 1200.ms),
        ],
      ),
    ).animate().fadeIn(delay: 500.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Seção de recompensas
  Widget _buildRewardsSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.orange.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const FaIcon(
                FontAwesomeIcons.gift,
                size: 20,
                color: Colors.orange,
              ),
              const SizedBox(width: 8),
              Text(
                'Recompensas de Sequência',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.white,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // XP ganho
          if (widget.rewardData.xpGained > 0) ...[
            _buildRewardRow(
              icon: FontAwesomeIcons.coins,
              label: 'XP',
              value: '+${widget.rewardData.xpGained}',
              color: AppColors.success,
              animation: LottieAnimations.coins(size: 20, repeat: true),
            ),
            if (widget.rewardData.pointsGained > 0) const SizedBox(height: 12),
          ],

          // Pontos ganhos
          if (widget.rewardData.pointsGained > 0)
            _buildRewardRow(
              icon: FontAwesomeIcons.star,
              label: 'Pontos',
              value: '+${widget.rewardData.pointsGained}',
              color: AppColors.gold,
              animation: LottieAnimations.stars(size: 20, repeat: true),
            ),
        ],
      ),
    ).animate().fadeIn(delay: 1400.ms).slideY(begin: 0.2, end: 0.0);
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
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(10),
          ),
          child: animation ??
              FaIcon(
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
              delay: 1600.ms,
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
                  Colors.orange,
                  Colors.deepOrange,
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: Colors.orange.withOpacity(0.4),
                  blurRadius: 12,
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
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
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
          ),
        ),

        // Botão de perfil (se disponível)
        if (widget.onViewProfile != null) ...[
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: Colors.orange.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: IconButton(
              onPressed: () {
                HapticFeedback.selectionClick();
                Navigator.of(context).pop();
                widget.onViewProfile?.call();
              },
              icon: const FaIcon(FontAwesomeIcons.user, size: 18),
              color: Colors.orange,
              tooltip: 'Ver Perfil',
            ),
          ),
        ],
      ],
    ).animate().fadeIn(delay: 1800.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Retorna título baseado na sequência
  String _getStreakTitle(int days) {
    if (days >= 30) return 'SEQUÊNCIA LENDÁRIA!';
    if (days >= 14) return 'SEQUÊNCIA ÉPICA!';
    if (days >= 7) return 'SEQUÊNCIA INCRÍVEL!';
    return 'SEQUÊNCIA ATIVA!';
  }

  /// Retorna subtítulo baseado na sequência
  String _getStreakSubtitle(int days) {
    if (days >= 30) return 'Você é uma lenda!';
    if (days >= 14) return 'Impressionante dedicação!';
    if (days >= 7) return 'Continue assim!';
    return 'Mantenha o ritmo!';
  }

  /// Retorna texto de sequência
  String _getStreakText(int days) {
    if (days >= 30) return 'LENDÁRIO!';
    if (days >= 14) return 'ÉPICO!';
    if (days >= 7) return 'INCRÍVEL!';
    return 'ATIVO!';
  }

  /// Retorna cor baseada na sequência
  Color _getStreakColor(int days) {
    if (days >= 30) return Colors.red;
    if (days >= 14) return Colors.deepOrange;
    if (days >= 7) return Colors.orange;
    return Colors.amber;
  }
}
