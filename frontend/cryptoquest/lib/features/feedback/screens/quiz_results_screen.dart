import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';
import 'package:cryptoquest/shared/widgets/enhanced_confetti_widget.dart';

/// Tela especializada para resultados de quiz
///
/// Tela dedicada para mostrar resultados de quiz com
/// feedback visual baseado na performance
class QuizResultsScreen extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;
  final VoidCallback? onViewProfile;

  const QuizResultsScreen({
    super.key,
    required this.rewardData,
    this.onContinue,
    this.onViewProfile,
  });

  /// Exibe a tela de Quiz Results
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.6),
      builder: (context) => QuizResultsScreen(
        rewardData: rewardData,
        onContinue: onContinue,
        onViewProfile: onViewProfile,
      ),
    );
  }

  @override
  State<QuizResultsScreen> createState() => _QuizResultsScreenState();
}

class _QuizResultsScreenState extends State<QuizResultsScreen>
    with TickerProviderStateMixin {
  late EnhancedConfettiController _confettiController;
  late AnimationController _lottieController;
  late AnimationController _progressController;

  @override
  void initState() {
    super.initState();

    _confettiController = EnhancedConfettiController();
    _lottieController = AnimationController(vsync: this);
    _progressController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );

    _triggerCelebration();
  }

  void _triggerCelebration() {
    final percentage = widget.rewardData.quizPercentage;

    // Haptic feedback baseado na performance
    if (percentage >= 90) {
      HapticFeedback.heavyImpact();
    } else if (percentage >= 70) {
      HapticFeedback.mediumImpact();
    } else {
      HapticFeedback.lightImpact();
    }

    // Iniciar animação de progresso
    _progressController.forward();

    // Confetti para performance excelente
    if (percentage >= 80) {
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
    _progressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;

    // Tela adaptável baseada na performance
    final percentage = widget.rewardData.quizPercentage;
    final maxHeight = percentage >= 90
        ? (screenHeight * 0.8).toDouble()
        : (screenHeight * 0.75).toDouble();
    final maxWidth = screenWidth > 600 ? 450.0 : (screenWidth * 0.9).toDouble();

    return Stack(
      children: [
        // Confetti de fundo (apenas para performance alta)
        if (percentage >= 80)
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
                  color: _getPerformanceColor(percentage).withOpacity(0.3),
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
                        // Animação Lottie baseada na performance
                        _buildPerformanceAnimation(),

                        const SizedBox(height: 24),

                        // Título principal
                        _buildMainTitle(),

                        const SizedBox(height: 20),

                        // Card de resultado principal
                        _buildResultCard(),

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
                begin: const Offset(0.5, 0.5),
                end: const Offset(1.0, 1.0),
                duration: 400.ms,
                curve: Curves.elasticOut,
              )
              .fadeIn(duration: 300.ms),
        ),
      ],
    );
  }

  /// Animação Lottie baseada na performance
  Widget _buildPerformanceAnimation() {
    final percentage = widget.rewardData.quizPercentage;
    Widget? lottieWidget;

    if (percentage >= 90) {
      lottieWidget = LottieAnimations.successCheck(
        size: 140,
        controller: _lottieController,
      );
    } else if (percentage >= 70) {
      lottieWidget = LottieAnimations.successCheck(
        size: 120,
        controller: _lottieController,
      );
    } else {
      lottieWidget = LottieAnimations.errorCross(
        size: 120,
        controller: _lottieController,
      );
    }

    return Center(
      child: lottieWidget,
    ).animate().fadeIn(duration: 300.ms).scale(
          begin: const Offset(0.3, 0.3),
          end: const Offset(1.0, 1.0),
          curve: Curves.elasticOut,
          duration: 600.ms,
        );
  }

  /// Título principal da tela
  Widget _buildMainTitle() {
    final percentage = widget.rewardData.quizPercentage;
    final title = _getPerformanceTitle(percentage);
    final subtitle = _getPerformanceSubtitle(percentage);

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

  /// Card de resultado principal
  Widget _buildResultCard() {
    final percentage = widget.rewardData.quizPercentage;
    final performanceColor = _getPerformanceColor(percentage);
    final isExcellent = percentage >= 90;
    final isGood = percentage >= 70;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: isExcellent || isGood
            ? LinearGradient(
                colors: [
                  performanceColor,
                  performanceColor.withOpacity(0.7),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : null,
        color: isExcellent || isGood ? null : AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: performanceColor.withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: performanceColor.withOpacity(0.2),
            blurRadius: 15,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        children: [
          // Ícone de performance
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: FaIcon(
              _getPerformanceIcon(percentage),
              size: 40,
              color: AppColors.white,
            ),
          ).animate().scale(
                begin: const Offset(0.0, 0.0),
                end: const Offset(1.0, 1.0),
                delay: 600.ms,
                curve: Curves.elasticOut,
              ),

          const SizedBox(height: 16),

          // Porcentagem animada
          AnimatedBuilder(
            animation: _progressController,
            builder: (context, child) {
              final animatedPercentage =
                  (_progressController.value * percentage).round();
              return Text(
                '$animatedPercentage%',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: AppColors.white,
                ),
              );
            },
          ).animate().fadeIn(delay: 800.ms),

          const SizedBox(height: 8),

          // Texto de performance
          Text(
            _getPerformanceText(percentage),
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.white,
            ),
          ).animate().fadeIn(delay: 1000.ms),

          const SizedBox(height: 4),

          Text(
            'de acertos no quiz',
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
          color: AppColors.primary.withOpacity(0.2),
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
                color: AppColors.primary,
              ),
              const SizedBox(width: 8),
              Text(
                'Recompensas Ganhas',
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
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.4),
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
              icon: const FaIcon(FontAwesomeIcons.user, size: 18),
              color: AppColors.primary,
              tooltip: 'Ver Perfil',
            ),
          ),
        ],
      ],
    ).animate().fadeIn(delay: 1800.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Retorna título baseado na performance
  String _getPerformanceTitle(double percentage) {
    if (percentage >= 90) return 'Excelente!';
    if (percentage >= 80) return 'Muito Bom!';
    if (percentage >= 70) return 'Bom Trabalho!';
    if (percentage >= 60) return 'Quase Lá!';
    return 'Continue Tentando!';
  }

  /// Retorna subtítulo baseado na performance
  String _getPerformanceSubtitle(double percentage) {
    if (percentage >= 90) return 'Performance excepcional!';
    if (percentage >= 80) return 'Você está indo muito bem!';
    if (percentage >= 70) return 'Boa performance!';
    if (percentage >= 60) return 'Você está melhorando!';
    return 'Não desista, você consegue!';
  }

  /// Retorna texto de performance
  String _getPerformanceText(double percentage) {
    if (percentage >= 90) return 'PERFEITO!';
    if (percentage >= 80) return 'EXCELENTE!';
    if (percentage >= 70) return 'MUITO BOM!';
    if (percentage >= 60) return 'BOM!';
    return 'TENTE NOVAMENTE';
  }

  /// Retorna ícone baseado na performance
  IconData _getPerformanceIcon(double percentage) {
    if (percentage >= 90) return FontAwesomeIcons.trophy;
    if (percentage >= 80) return FontAwesomeIcons.star;
    if (percentage >= 70) return FontAwesomeIcons.thumbsUp;
    if (percentage >= 60) return FontAwesomeIcons.thumbsUp;
    return FontAwesomeIcons.rotateRight;
  }

  /// Retorna cor baseada na performance
  Color _getPerformanceColor(double percentage) {
    if (percentage >= 90) return AppColors.gold;
    if (percentage >= 80) return AppColors.success;
    if (percentage >= 70) return AppColors.info;
    if (percentage >= 60) return AppColors.warning;
    return AppColors.error;
  }
}
